from datetime import datetime

import pandas as pd

from broker.base import Fill
from broker.mock_broker import MockBroker
from engine import run_paper_trading
from portfolio.portfolio import Portfolio
from risk.risk_manager import RiskManager
from strategy.signal import MovingAverageStrategy


def test_strategy_waits_for_slow_window_and_turns_long_on_uptrend():
    strategy = MovingAverageStrategy(fast_window=2, slow_window=4)
    assert strategy.on_price(100) is None
    assert strategy.on_price(101) is None
    assert strategy.on_price(102) is None
    assert strategy.on_price(103) == 1


def test_portfolio_realizes_pnl_when_long_is_closed():
    portfolio = Portfolio(contract_multiplier=10)
    portfolio.apply_fill(Fill("1", "X", "BUY", 1, 100.0, datetime(2026, 1, 1)))
    portfolio.apply_fill(Fill("2", "X", "SELL", 1, 102.0, datetime(2026, 1, 2)))
    assert portfolio.position == 0
    assert portfolio.realized_pnl == 20.0
    assert portfolio.average_price == 0.0


def test_daily_loss_limit_blocks_new_risk_but_allows_closing():
    risk = RiskManager(max_abs_position=1, max_daily_loss=5.0)
    blocked = risk.evaluate(current_position=0, target_position=1, daily_pnl=-5.0)
    closing = risk.evaluate(current_position=1, target_position=0, daily_pnl=-5.0)
    assert blocked.allowed is False
    assert blocked.reason == "daily_loss_limit"
    assert closing.allowed is True


def test_paper_trading_engine_runs_end_to_end():
    market = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=30, freq="h"),
            "close": [100 + i * 0.5 for i in range(15)] + [107 - i * 0.6 for i in range(15)],
        }
    )
    states, trades = run_paper_trading(
        market_data=market,
        symbol="MOCK-FUT",
        strategy=MovingAverageStrategy(3, 6),
        broker=MockBroker(),
        portfolio=Portfolio(),
        risk_manager=RiskManager(max_abs_position=1, max_daily_loss=1000),
    )
    assert len(states) == len(market)
    assert not trades.empty
    assert set(states["position"].dropna().unique()).issubset({-1, 0, 1})
