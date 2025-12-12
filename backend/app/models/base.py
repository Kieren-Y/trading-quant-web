from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.sql import func

from app.core.db import Base


class TimeStampMixin:
    """Mixin to add created_at and updated_at columns."""

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )


class User(Base, TimeStampMixin):
    """User model for authentication."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)


class ExchangeConfig(Base, TimeStampMixin):
    """Configuration for exchange accounts (API keys)."""

    __tablename__ = "exchange_configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exchange_name = Column(String, nullable=False)  # e.g., "binance", "okx"
    api_key = Column(String, nullable=False)  # Should be encrypted in real app
    secret_key = Column(String, nullable=False)  # Should be encrypted
    account_name = Column(String, nullable=True)  # User defined name
    is_active = Column(Boolean, default=True)


class StrategyConfig(Base, TimeStampMixin):
    """Configuration for trading strategies."""

    __tablename__ = "strategy_configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    strategy_name = Column(String, nullable=False)  # e.g., "grid_trading"
    parameters = Column(JSON, nullable=False)  # JSON blob for strategy params
    status = Column(String, default="stopped")  # stopped, running, error
    exchange_config_id = Column(
        Integer, ForeignKey("exchange_configs.id"), nullable=True
    )


class Order(Base, TimeStampMixin):
    """Order history."""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    exchange_order_id = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exchange_config_id = Column(
        Integer, ForeignKey("exchange_configs.id"), nullable=False
    )
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)  # buy, sell
    type = Column(String, nullable=False)  # limit, market
    price = Column(Float, nullable=True)
    amount = Column(Float, nullable=False)
    status = Column(String, nullable=False)  # open, closed, canceled
    filled = Column(Float, default=0.0)
    cost = Column(Float, default=0.0)
