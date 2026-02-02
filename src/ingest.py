from __future__ import annotations

from pathlib import Path
from typing import Dict
import pandas as pd


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing input: {path}")
    return pd.read_csv(path)


def load_inputs(root: Path) -> Dict[str, pd.DataFrame]:
    raw = root / "inputs" / "raw"
    subs = load_csv(raw / "subscriptions_monthly.csv")
    usage = load_csv(raw / "usage_monthly.csv")
    cogs_ai = load_csv(raw / "cogs_ai_monthly.csv")
    opex = load_csv(raw / "opex_monthly.csv")
    cash = load_csv(raw / "cash_monthly.csv")

    # Normalize month
    for df in [subs, usage, cogs_ai, opex, cash]:
        if "month" in df.columns:
            df["month"] = df["month"].astype(str)

    return {
        "subs": subs,
        "usage": usage,
        "cogs_ai": cogs_ai,
        "opex": opex,
        "cash": cash,
    }
