from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.schemas.asset import PortfolioSummary
from app.services.asset_service import AssetService

router = APIRouter()


# TODO: Replace with real user dependency
async def get_current_user_id():
    return 1


@router.get("/", response_model=PortfolioSummary)
async def get_assets(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    service = AssetService(db)
    return await service.get_portfolio_summary(user_id)
