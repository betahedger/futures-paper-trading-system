from __future__ import annotations

from broker.base import Fill


class Portfolio:
    def __init__(self, contract_multiplier: float = 1.0) -> None:
        if contract_multiplier <= 0:
            raise ValueError("contract_multiplier must be positive")
        self.multiplier = float(contract_multiplier)
        self.position = 0
        self.average_price = 0.0
        self.realized_pnl = 0.0

    def apply_fill(self, fill: Fill) -> None:
        signed = fill.signed_quantity
        old_position = self.position
        new_position = old_position + signed

        if old_position == 0 or old_position * signed > 0:
            old_qty = abs(old_position)
            added_qty = abs(signed)
            self.average_price = (
                (self.average_price * old_qty + fill.price * added_qty)
                / (old_qty + added_qty)
            )
        else:
            closing_qty = min(abs(old_position), abs(signed))
            if old_position > 0:
                self.realized_pnl += (
                    fill.price - self.average_price
                ) * closing_qty * self.multiplier
            else:
                self.realized_pnl += (
                    self.average_price - fill.price
                ) * closing_qty * self.multiplier

            if new_position == 0:
                self.average_price = 0.0
            elif old_position * new_position < 0:
                self.average_price = fill.price

        self.position = new_position

    def unrealized_pnl(self, market_price: float) -> float:
        if self.position > 0:
            return (market_price - self.average_price) * self.position * self.multiplier
        if self.position < 0:
            return (self.average_price - market_price) * abs(self.position) * self.multiplier
        return 0.0

    def total_pnl(self, market_price: float) -> float:
        return self.realized_pnl + self.unrealized_pnl(market_price)
