from __future__ import annotations

import argparse

from broker.mock_broker import MockBroker
from config import TradingConfig
from data.market_data import load_market_data
from engine import run_paper_trading, save_results
from portfolio.portfolio import Portfolio
from risk.risk_manager import RiskManager
from strategy.signal import MovingAverageStrategy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Futures paper-trading simulation")
    parser.add_argument("--csv", default="data/sample_market.csv")
    parser.add_argument("--symbol", default="MOCK-FUT")
    parser.add_argument("--fast", type=int, default=5)
    parser.add_argument("--slow", type=int, default=20)
    parser.add_argument("--max-position", type=int, default=1)
    parser.add_argument("--max-daily-loss", type=float, default=5.0)
    parser.add_argument("--multiplier", type=float, default=1.0)
    parser.add_argument("--output-dir", default="results")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = TradingConfig(
        symbol=args.symbol,
        fast_window=args.fast,
        slow_window=args.slow,
        max_abs_position=args.max_position,
        max_daily_loss=args.max_daily_loss,
        contract_multiplier=args.multiplier,
    )

    market_data = load_market_data(args.csv)
    strategy = MovingAverageStrategy(config.fast_window, config.slow_window)
    broker = MockBroker()
    portfolio = Portfolio(config.contract_multiplier)
    risk_manager = RiskManager(config.max_abs_position, config.max_daily_loss)

    states, trades = run_paper_trading(
        market_data=market_data,
        symbol=config.symbol,
        strategy=strategy,
        broker=broker,
        portfolio=portfolio,
        risk_manager=risk_manager,
    )
    save_results(states, trades, args.output_dir)

    last_price = float(states.iloc[-1]["close"])
    print("Paper trading simulation complete")
    print(f"Rows             : {len(states)}")
    print(f"Trades           : {len(trades)}")
    print(f"Final position   : {portfolio.position}")
    print(f"Realized PnL     : {portfolio.realized_pnl:.2f}")
    print(f"Unrealized PnL   : {portfolio.unrealized_pnl(last_price):.2f}")
    print(f"Total PnL        : {portfolio.total_pnl(last_price):.2f}")
    print(f"Saved results to : {args.output_dir}")


if __name__ == "__main__":
    main()
