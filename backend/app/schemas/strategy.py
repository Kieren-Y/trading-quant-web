from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict


class StrategyConfigBase(BaseModel):
    strategy_name: str
    exchange_config_id: int
    parameters: Dict[str, Any]  # JSON blob


class StrategyConfigCreate(StrategyConfigBase):
    pass


class StrategyConfigUpdate(BaseModel):
    parameters: Optional[Dict[str, Any]] = None
    status: Optional[str] = None  # running, stopped, error


class StrategyConfigResponse(StrategyConfigBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
