from __future__ import annotations

from collections import deque


class MovingAverageStrategy:
    """단순 이동평균 교차로 목표 포지션(-1, 0, +1)을 생성한다."""

    def __init__(self, fast_window: int = 5, slow_window: int = 20) -> None:
        if fast_window <= 0 or slow_window <= 0:
            raise ValueError("moving-average windows must be positive")
        if fast_window >= slow_window:
            raise ValueError("fast_window must be smaller than slow_window")
        self.fast_window = fast_window
        self.slow_window = slow_window
        self._prices: deque[float] = deque(maxlen=slow_window)

    def on_price(self, price: float) -> int | None:
        self._prices.append(float(price))
        if len(self._prices) < self.slow_window:
            return None

        prices = list(self._prices)
        fast = sum(prices[-self.fast_window :]) / self.fast_window
        slow = sum(prices) / self.slow_window
        if fast > slow:
            return 1
        if fast < slow:
            return -1
        return 0
