import asyncio
from typing import Any, Dict, Optional

import ccxt.async_support as ccxt

from app.models.base import ExchangeConfig


class CCXTService:
    _instances: Dict[str, ccxt.Exchange] = {}

    @classmethod
    async def get_exchange(cls, config: ExchangeConfig) -> ccxt.Exchange:
        """
        Get or create a CCXT exchange instance.
        Note: In a production environment, you might want to handle instance caching more robustly,
        considering API key updates and thread safety.
        """
        instance_key = f"{config.exchange_name}_{config.api_key}"

        if instance_key in cls._instances:
            return cls._instances[instance_key]

        exchange_class = getattr(ccxt, config.exchange_name)
        exchange = exchange_class(
            {
                "apiKey": config.api_key,
                "secret": config.secret_key,
                "enableRateLimit": True,
                "options": {
                    "defaultType": "future"
                },  # Default to futures for quant trading usually
            }
        )

        # Verify connection (optional but good for debugging)
        # await exchange.load_markets()

        cls._instances[instance_key] = exchange
        return exchange

    @classmethod
    async def close_all(cls):
        for exchange in cls._instances.values():
            await exchange.close()
        cls._instances.clear()

    @staticmethod
    async def fetch_balance(
        config: ExchangeConfig, market_type: str = "spot"
    ) -> Dict[str, Any]:
        try:
            exchange = await CCXTService.get_exchange(config)

            # Switch market type options
            # Note: This is a bit tricky with singleton instances if concurrently accessed with different types
            # For a proper implementation, we might need different instances for different types or use parameters

            # Create a temporary params dict for the call if possible, but fetch_balance usually relies on exchange properties
            # For CCXT, changing options['defaultType'] works for many exchanges
            exchange.options["defaultType"] = market_type

            balance = await exchange.fetch_balance()
            print(f"DEBUG: Fetched {market_type} balance for {config.exchange_name}")
            return balance
        except Exception as e:
            # Some exchanges might not support the requested type, just return empty
            print(
                f"Error fetching {market_type} balance for {config.exchange_name}: {str(e)}"
            )
            return {}

    @staticmethod
    async def fetch_ticker(config: ExchangeConfig, symbol: str) -> Dict[str, Any]:
        try:
            exchange = await CCXTService.get_exchange(config)
            ticker = await exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            print(
                f"Error fetching ticker for {config.exchange_name} {symbol}: {str(e)}"
            )
            return {}
