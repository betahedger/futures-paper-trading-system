from __future__ import annotations

from datetime import datetime

from .base import Broker, Fill


class MockBroker(Broker):
    """시장가 주문이 현재 표시가격에서 즉시 체결된다고 가정하는 모의 브로커."""

    def __init__(self) -> None:
        self._prices: dict[str, float] = {}
        self._positions: dict[str, int] = {}
        self._order_count = 0
        self.fills: list[Fill] = []

    def update_market(self, symbol: str, price: float) -> None:
        if price <= 0:
            raise ValueError("price must be positive")
        self._prices[symbol] = float(price)

    def get_price(self, symbol: str) -> float:
        if symbol not in self._prices:
            raise RuntimeError(f"no market price for {symbol}")
        return self._prices[symbol]

    def get_position(self, symbol: str) -> int:
        return self._positions.get(symbol, 0)

    def place_market_order(
        self,
        symbol: str,
        side: str,
        quantity: int,
        timestamp: datetime,
    ) -> Fill:
        side = side.upper()
        if side not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")
        if quantity <= 0:
            raise ValueError("quantity must be positive")

        price = self.get_price(symbol)
        self._order_count += 1
        fill = Fill(
            order_id=f"MOCK-{self._order_count:05d}",
            symbol=symbol,
            side=side,
            quantity=int(quantity),
            price=price,
            timestamp=timestamp,
        )
        self._positions[symbol] = self.get_position(symbol) + fill.signed_quantity
        self.fills.append(fill)
        return fill
