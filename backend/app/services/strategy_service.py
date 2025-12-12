from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.base import StrategyConfig
from app.schemas.strategy import StrategyConfigCreate, StrategyConfigUpdate
from app.strategies.base import BaseStrategy, SimpleGridStrategy


class StrategyService:
    # In-memory registry of running strategies
    # {strategy_id: StrategyInstance}
    _running_strategies: Dict[int, BaseStrategy] = {}

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, user_id: int) -> List[StrategyConfig]:
        query = select(StrategyConfig).where(StrategyConfig.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_id(
        self, strategy_id: int, user_id: int
    ) -> Optional[StrategyConfig]:
        query = select(StrategyConfig).where(
            StrategyConfig.id == strategy_id, StrategyConfig.user_id == user_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(
        self, user_id: int, config: StrategyConfigCreate
    ) -> StrategyConfig:
        db_obj = StrategyConfig(
            user_id=user_id,
            strategy_name=config.strategy_name,
            exchange_config_id=config.exchange_config_id,
            parameters=config.parameters,
            status="stopped",
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self, strategy_id: int, user_id: int, config: StrategyConfigUpdate
    ) -> Optional[StrategyConfig]:
        db_obj = await self.get_by_id(strategy_id, user_id)
        if not db_obj:
            return None

        update_data = config.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, strategy_id: int, user_id: int) -> bool:
        db_obj = await self.get_by_id(strategy_id, user_id)
        if not db_obj:
            return False

        # Stop if running
        await self.stop_strategy(strategy_id, user_id)

        await self.db.delete(db_obj)
        await self.db.commit()
        return True

    async def start_strategy(self, strategy_id: int, user_id: int) -> bool:
        db_obj = await self.get_by_id(strategy_id, user_id)
        if not db_obj:
            return False

        if strategy_id in self._running_strategies:
            return True  # Already running

        # Initialize strategy instance
        # In a real app, we would factory this based on strategy_name
        strategy_instance = SimpleGridStrategy(
            config={
                "id": db_obj.id,
                "parameters": db_obj.parameters,
                "user_id": user_id,
            }
        )

        await strategy_instance.start()
        self._running_strategies[strategy_id] = strategy_instance

        # Update DB status
        db_obj.status = "running"
        await self.db.commit()

        return True

    async def stop_strategy(self, strategy_id: int, user_id: int) -> bool:
        db_obj = await self.get_by_id(strategy_id, user_id)
        if not db_obj:
            return False

        if strategy_id in self._running_strategies:
            instance = self._running_strategies[strategy_id]
            await instance.stop()
            del self._running_strategies[strategy_id]

        # Update DB status
        db_obj.status = "stopped"
        await self.db.commit()

        return True
