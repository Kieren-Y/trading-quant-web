from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class OrderBase(BaseModel):
    exchange_config_id: int
    symbol: str
    side: str  # buy, sell
    type: str  # limit, market
    price: Optional[float] = None
    amount: float
    market_type: str = "spot"  # spot, future


class OrderCreate(OrderBase):
    pass


class OrderResponse(OrderBase):
    id: int
    user_id: int
    exchange_order_id: Optional[str] = None
    status: str  # open, closed, canceled, failed
    filled: float = 0.0
    cost: float = 0.0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
