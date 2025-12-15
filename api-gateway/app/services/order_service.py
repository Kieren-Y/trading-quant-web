from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.base import Order
from app.schemas.order import OrderCreate
from app.services.ccxt_service import CCXTService
from app.services.exchange_service import ExchangeConfigService


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.exchange_service = ExchangeConfigService(db)

    async def create_order(self, user_id: int, order_in: OrderCreate) -> Order:
        # 1. Get Exchange Config
        config = await self.exchange_service.get_by_id(
            order_in.exchange_config_id, user_id
        )
        if not config:
            raise ValueError("Exchange config not found")

        # 2. Execute on Exchange via CCXT
        exchange = await CCXTService.get_exchange(config)

        # Set market type context
        exchange.options["defaultType"] = order_in.market_type

        try:
            params = {}
            # Basic validation for Limit orders
            if order_in.type == "limit" and not order_in.price:
                raise ValueError("Price is required for limit orders")

            ccxt_order = await exchange.create_order(
                symbol=order_in.symbol,
                type=order_in.type,
                side=order_in.side,
                amount=order_in.amount,
                price=order_in.price,
                params=params,
            )

            exchange_order_id = str(ccxt_order["id"])
            status = ccxt_order.get("status", "open")
            filled = ccxt_order.get("filled", 0.0)
            cost = ccxt_order.get("cost", 0.0)

        except Exception as e:
            # If exchange call fails, we might still want to log it or just raise
            # For now, we raise to let the API handle the error response
            print(f"Order Execution Failed: {str(e)}")
            raise e

        # 3. Save to Database
        db_order = Order(
            user_id=user_id,
            exchange_config_id=order_in.exchange_config_id,
            exchange_order_id=exchange_order_id,
            symbol=order_in.symbol,
            side=order_in.side,
            type=order_in.type,
            price=order_in.price,
            amount=order_in.amount,
            status=status,
            filled=filled,
            cost=cost or 0.0,
        )

        self.db.add(db_order)
        await self.db.commit()
        await self.db.refresh(db_order)
        return db_order

    async def get_orders(self, user_id: int, limit: int = 50) -> List[Order]:
        query = (
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def cancel_order(self, user_id: int, order_id: int) -> bool:
        # 1. Get Order from DB
        query = select(Order).where(Order.id == order_id, Order.user_id == user_id)
        result = await self.db.execute(query)
        order = result.scalar_one_or_none()

        if not order:
            return False

        if order.status in ["closed", "canceled"]:
            return True  # Already done

        # 2. Get Exchange Config
        config = await self.exchange_service.get_by_id(
            order.exchange_config_id, user_id
        )
        if not config:
            return False

        # 3. Execute Cancel on Exchange
        try:
            exchange = await CCXTService.get_exchange(config)
            # Need to know market type to cancel correctly usually,
            # but MVP schema didn't save market_type in DB (Oversight in Phase 1)
            # We'll assume 'spot' or try to infer, or just try canceling.
            # TODO: Add market_type to Order model in DB migration

            # For now, try default (which might be spot or future depending on last set options)
            # Safest is to try to match what the user likely used.
            # Let's default to future if it looks like a perp symbol, else spot.
            if ":" in order.symbol:  # e.g. BTC/USDT:USDT
                exchange.options["defaultType"] = "future"
            else:
                exchange.options["defaultType"] = "spot"

            await exchange.cancel_order(order.exchange_order_id, order.symbol)

            # Update DB
            order.status = "canceled"
            await self.db.commit()
            return True

        except Exception as e:
            print(f"Cancel Failed: {str(e)}")
            return False
