from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskDecision:
    allowed: bool
    reason: str


class RiskManager:
    def __init__(self, max_abs_position: int = 1, max_daily_loss: float = 5.0) -> None:
        if max_abs_position <= 0:
            raise ValueError("max_abs_position must be positive")
        if max_daily_loss <= 0:
            raise ValueError("max_daily_loss must be positive")
        self.max_abs_position = int(max_abs_position)
        self.max_daily_loss = float(max_daily_loss)

    def evaluate(
        self,
        current_position: int,
        target_position: int,
        daily_pnl: float,
    ) -> RiskDecision:
        if abs(target_position) > self.max_abs_position:
            return RiskDecision(False, "position_limit")

        loss_limit_hit = daily_pnl <= -self.max_daily_loss
        reducing_risk = abs(target_position) < abs(current_position) or target_position == 0
        if loss_limit_hit and not reducing_risk:
            return RiskDecision(False, "daily_loss_limit")

        return RiskDecision(True, "ok")
