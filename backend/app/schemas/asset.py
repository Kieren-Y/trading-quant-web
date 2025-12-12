from typing import Dict, List

from pydantic import BaseModel


class AssetBalance(BaseModel):
    currency: str
    free: float
    used: float
    total: float
    usdt_value: float = 0.0  # Estimated value in USDT


class ExchangeAsset(BaseModel):
    exchange_name: str
    account_name: str
    market_type: str = "spot"  # spot, future, margin, etc.
    total_usdt_value: float
    balances: List[AssetBalance]


class PortfolioSummary(BaseModel):
    total_usdt_value: float
    exchanges: List[ExchangeAsset]
