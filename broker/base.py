from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Fill:
    order_id: str
    symbol: str
    side: str
    quantity: int
    price: float
    timestamp: datetime

    @property
    def signed_quantity(self) -> int:
        return self.quantity if self.side == "BUY" else -self.quantity


class Broker(ABC):
    @abstractmethod
    def get_price(self, symbol: str) -> float:
        raise NotImplementedError

    @abstractmethod
    def get_position(self, symbol: str) -> int:
        raise NotImplementedError

    @abstractmethod
    def place_market_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        timestamp: datetime,
    ) -> Fill:
        raise NotImplementedError
