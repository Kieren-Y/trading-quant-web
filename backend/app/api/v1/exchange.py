from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.schemas.exchange import (
    ExchangeConfigCreate,
    ExchangeConfigResponse,
    ExchangeConfigUpdate,
)
from app.services.exchange_service import ExchangeConfigService

router = APIRouter()


# TODO: Replace with real user dependency
async def get_current_user_id():
    return 1  # Mock user ID for MVP


@router.get("/", response_model=List[ExchangeConfigResponse])
async def get_exchange_configs(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service = ExchangeConfigService(db)
    return await service.get_all(user_id)


@router.post("/", response_model=ExchangeConfigResponse)
async def create_exchange_config(
    config: ExchangeConfigCreate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service = ExchangeConfigService(db)
    return await service.create(user_id, config)


@router.put("/{config_id}", response_model=ExchangeConfigResponse)
async def update_exchange_config(
    config_id: int,
    config: ExchangeConfigUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service = ExchangeConfigService(db)
    updated_config = await service.update(config_id, user_id, config)
    if not updated_config:
        raise HTTPException(status_code=404, detail="Exchange config not found")
    return updated_config


@router.delete("/{config_id}")
async def delete_exchange_config(
    config_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service = ExchangeConfigService(db)
    success = await service.delete(config_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Exchange config not found")
    return {"status": "success"}
