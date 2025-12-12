from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.schemas.strategy import (
    StrategyConfigCreate,
    StrategyConfigResponse,
    StrategyConfigUpdate,
)
from app.services.strategy_service import StrategyService

router = APIRouter()


# TODO: Replace with real user dependency
async def get_current_user_id():
    return 1


@router.get("/", response_model=List[StrategyConfigResponse])
async def get_strategies(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service = StrategyService(db)
    return await service.get_all(user_id)


@router.post("/", response_model=StrategyConfigResponse)
async def create_strategy(
    config: StrategyConfigCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service = StrategyService(db)
    return await service.create(user_id, config)


@router.put("/{strategy_id}", response_model=StrategyConfigResponse)
async def update_strategy(
    strategy_id: int,
    config: StrategyConfigUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service = StrategyService(db)
    updated = await service.update(strategy_id, user_id, config)
    if not updated:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return updated


@router.delete("/{strategy_id}")
async def delete_strategy(
    strategy_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service = StrategyService(db)
    success = await service.delete(strategy_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return {"status": "success"}


@router.post("/{strategy_id}/start")
async def start_strategy(
    strategy_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service = StrategyService(db)
    success = await service.start_strategy(strategy_id, user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to start strategy")
    return {"status": "started"}


@router.post("/{strategy_id}/stop")
async def stop_strategy(
    strategy_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service = StrategyService(db)
    success = await service.stop_strategy(strategy_id, user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to stop strategy")
    return {"status": "stopped"}
