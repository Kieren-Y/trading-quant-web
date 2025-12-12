from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.base import ExchangeConfig
from app.schemas.exchange import ExchangeConfigCreate, ExchangeConfigUpdate


class ExchangeConfigService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, user_id: int) -> List[ExchangeConfig]:
        query = select(ExchangeConfig).where(ExchangeConfig.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_id(self, config_id: int, user_id: int) -> Optional[ExchangeConfig]:
        query = select(ExchangeConfig).where(
            ExchangeConfig.id == config_id, ExchangeConfig.user_id == user_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(
        self, user_id: int, config: ExchangeConfigCreate
    ) -> ExchangeConfig:
        db_obj = ExchangeConfig(
            user_id=user_id,
            exchange_name=config.exchange_name,
            api_key=config.api_key,
            secret_key=config.secret_key,
            account_name=config.account_name,
            is_active=config.is_active,
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self, config_id: int, user_id: int, config: ExchangeConfigUpdate
    ) -> Optional[ExchangeConfig]:
        db_obj = await self.get_by_id(config_id, user_id)
        if not db_obj:
            return None

        update_data = config.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, config_id: int, user_id: int) -> bool:
        db_obj = await self.get_by_id(config_id, user_id)
        if not db_obj:
            return False

        await self.db.delete(db_obj)
        await self.db.commit()
        return True
