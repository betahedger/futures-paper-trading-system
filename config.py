from dataclasses import dataclass


@dataclass(frozen=True)
class TradingConfig:
    symbol: str = "MOCK-FUT"
    fast_window: int = 5
    slow_window: int = 20
    max_abs_position: int = 1
    max_daily_loss: float = 5.0
    contract_multiplier: float = 1.0
