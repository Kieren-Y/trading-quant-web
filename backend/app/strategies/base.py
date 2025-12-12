import asyncio
from typing import Any, Dict, Optional


class BaseStrategy:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_running = False

    async def start(self):
        self.is_running = True
        print(f"Strategy {self.__class__.__name__} started with config: {self.config}")
        asyncio.create_task(self.run_loop())

    async def stop(self):
        self.is_running = False
        print(f"Strategy {self.__class__.__name__} stopping...")

    async def run_loop(self):
        while self.is_running:
            try:
                await self.tick()
                await asyncio.sleep(5)  # Default 5s interval
            except Exception as e:
                print(f"Strategy error: {e}")
                await asyncio.sleep(5)

    async def tick(self):
        raise NotImplementedError("Strategy must implement tick method")


class SimpleGridStrategy(BaseStrategy):
    """
    A Mock Grid Strategy for MVP.
    Real implementation would calculate grid levels and place orders.
    """

    async def tick(self):
        # Mock logic: Print price or something
        # In real app, we would use CCXTService to fetch price and OrderService to place orders
        symbol = self.config.get("parameters", {}).get("symbol", "UNKNOWN")
        print(f"Grid Strategy Tick: Checking {symbol}...")
