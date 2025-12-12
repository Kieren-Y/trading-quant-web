from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.asset import AssetBalance, ExchangeAsset, PortfolioSummary
from app.services.ccxt_service import CCXTService
from app.services.exchange_service import ExchangeConfigService


class AssetService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.exchange_service = ExchangeConfigService(db)

    async def get_portfolio_summary(self, user_id: int) -> PortfolioSummary:
        configs = await self.exchange_service.get_all(user_id)

        exchange_assets = []
        total_portfolio_value = 0.0

        for config in configs:
            if not config.is_active:
                continue

            # We want to fetch both Spot and Future balances
            # For simplicity, we hardcode these types for now.
            # In a real app, this might be configurable per exchange.
            target_types = ["spot", "future"]
            if config.exchange_name == "okx":
                target_types = [
                    "spot",
                    "swap",
                ]  # OKX uses 'swap' for perpetuals usually

            for market_type in target_types:
                raw_balance = await CCXTService.fetch_balance(
                    config, market_type=market_type
                )

                # Parse raw balance
                balances: List[AssetBalance] = []
                exchange_total_value = 0.0

                # Process 'total' dictionary
                if "total" in raw_balance:
                    for currency, total_amount in raw_balance["total"].items():
                        if total_amount == 0:
                            continue

                        free = raw_balance.get("free", {}).get(currency, 0.0)
                        used = raw_balance.get("used", {}).get(currency, 0.0)

                        # Estimate USDT Value (Very simplified for MVP)
                        usdt_value = 0.0
                        if currency == "USDT":
                            usdt_value = total_amount

                        # Log if we are skipping non-zero balance
                        if total_amount > 0:
                            print(
                                f"DEBUG: Found {config.exchange_name} {market_type} {currency}: {total_amount}"
                            )

                        exchange_total_value += usdt_value

                        balances.append(
                            AssetBalance(
                                currency=currency,
                                free=free,
                                used=used,
                                total=total_amount,
                                usdt_value=usdt_value,
                            )
                        )

                # Only add if there are balances or if it's a valid empty account
                if balances or market_type == "spot":
                    exchange_assets.append(
                        ExchangeAsset(
                            exchange_name=config.exchange_name,
                            account_name=config.account_name or config.exchange_name,
                            market_type=market_type,
                            total_usdt_value=exchange_total_value,
                            balances=balances,
                        )
                    )
                    total_portfolio_value += exchange_total_value

        return PortfolioSummary(
            total_usdt_value=total_portfolio_value, exchanges=exchange_assets
        )
