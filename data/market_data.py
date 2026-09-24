from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_market_data(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    required = {"timestamp", "close"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")

    out = frame[["timestamp", "close"]].copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"])
    out["close"] = pd.to_numeric(out["close"], errors="raise")
    if (out["close"] <= 0).any():
        raise ValueError("close prices must be positive")
    return out.sort_values("timestamp").drop_duplicates("timestamp").reset_index(drop=True)
