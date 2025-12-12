from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import OrderService

router = APIRouter()


# TODO: Replace with real user dependency
async def get_current_user_id():
    return 1


@router.post("/", response_model=OrderResponse)
async def create_order(
    order_in: OrderCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service = OrderService(db)
    try:
        return await service.create_order(user_id, order_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exchange error: {str(e)}")


@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service = OrderService(db)
    return await service.get_orders(user_id)


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service = OrderService(db)
    success = await service.cancel_order(user_id, order_id)
    if not success:
        raise HTTPException(
            status_code=400, detail="Failed to cancel order or order not found"
        )
    return {"status": "success"}
