from __future__ import annotations

import pandas as pd


def mrr_bridge(df: pd.DataFrame) -> pd.DataFrame:
    # Simple bridge: delta MRR split into seat vs usage movement
    d = df.sort_values("month").copy()
    d["prev_mrr"] = d["mrr"].shift(1)
    d["delta_mrr"] = d["mrr"] - d["prev_mrr"]
    d["delta_seat"] = d["seat_mrr"].diff()
    d["delta_usage"] = d["usage_mrr"].diff()
    out = d[["month", "prev_mrr", "mrr", "delta_mrr", "delta_seat", "delta_usage"]].dropna()
    return out


def gm_bridge(df: pd.DataFrame) -> pd.DataFrame:
    d = df.sort_values("month").copy()
    d["prev_gm"] = d["gross_margin_pct"].shift(1)
    d["delta_gm"] = d["gross_margin_pct"] - d["prev_gm"]
    out = d[["month", "prev_gm", "gross_margin_pct", "delta_gm"]].dropna()
    return out
