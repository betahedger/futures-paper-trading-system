from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import pandas as pd

from broker.mock_broker import MockBroker
from portfolio.portfolio import Portfolio
from risk.risk_manager import RiskManager
from strategy.signal import MovingAverageStrategy


def run_paper_trading(
    market_data: pd.DataFrame,
    symbol: str,
    strategy: MovingAverageStrategy,
    broker: MockBroker,
    portfolio: Portfolio,
    risk_manager: RiskManager,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    state_rows: list[dict] = []
    trade_rows: list[dict] = []
    current_date = None
    day_start_total_pnl = 0.0

    for row in market_data.itertuples(index=False):
        timestamp = pd.Timestamp(row.timestamp).to_pydatetime()
        price = float(row.close)
        broker.update_market(symbol, price)

        if current_date != timestamp.date():
            current_date = timestamp.date()
            day_start_total_pnl = portfolio.total_pnl(price)

        target = strategy.on_price(price)
        total_before_order = portfolio.total_pnl(price)
        daily_pnl = total_before_order - day_start_total_pnl
        risk_reason = "no_signal"

        if target is not None and target != portfolio.position:
            decision = risk_manager.evaluate(
                current_position=portfolio.position,
                target_position=target,
                daily_pnl=daily_pnl,
            )
            risk_reason = decision.reason
            if decision.allowed:
                delta = target - portfolio.position
                side = "BUY" if delta > 0 else "SELL"
                fill = broker.place_market_order(
                    symbol=symbol,
                    side=side,
                    quantity=abs(delta),
                    timestamp=timestamp,
                )
                portfolio.apply_fill(fill)
                trade_rows.append(asdict(fill))
        elif target is not None:
            risk_reason = "position_unchanged"

        state_rows.append(
            {
                "timestamp": timestamp,
                "close": price,
                "target_position": target,
                "position": portfolio.position,
                "average_price": portfolio.average_price,
                "realized_pnl": portfolio.realized_pnl,
                "unrealized_pnl": portfolio.unrealized_pnl(price),
                "total_pnl": portfolio.total_pnl(price),
                "risk_status": risk_reason,
            }
        )

    states = pd.DataFrame(state_rows)
    trades = pd.DataFrame(trade_rows)
    return states, trades


def save_results(states: pd.DataFrame, trades: pd.DataFrame, output_dir: str | Path) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    states.to_csv(output_dir / "paper_trading_log.csv", index=False)
    trades.to_csv(output_dir / "trades.csv", index=False)
