from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ExchangeConfigBase(BaseModel):
    exchange_name: str
    api_key: str
    secret_key: str
    account_name: Optional[str] = None
    is_active: bool = True


class ExchangeConfigCreate(ExchangeConfigBase):
    pass


class ExchangeConfigUpdate(BaseModel):
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    account_name: Optional[str] = None
    is_active: Optional[bool] = None


class ExchangeConfigResponse(ExchangeConfigBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    # Hide secret key in response for security
    secret_key: str = "***"

    model_config = ConfigDict(from_attributes=True)
