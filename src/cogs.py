from __future__ import annotations

import pandas as pd


def add_cogs(kpis: pd.DataFrame, cogs_ai: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    df = kpis.merge(cogs_ai, on="month", how="left").fillna(0)

    mult = float(cfg.get("cost_per_1k_tokens_mult", 1.0))
    df["cost_per_1k_tokens"] = df["cost_per_1k_tokens"] * mult

    tokens_total = df["tokens_in"] + df["tokens_out"]
    df["ai_cogs"] = (tokens_total / 1000.0) * df["cost_per_1k_tokens"] + df["infra_fixed_cost"]

    other_pct = float(cfg.get("cogs_other_percent_of_revenue", 0.0))
    df["other_cogs"] = df["mrr"] * other_pct
    df["total_cogs"] = df["ai_cogs"] + df["other_cogs"]

    df["gross_profit"] = df["mrr"] - df["total_cogs"]
    df["gross_margin_pct"] = (df["gross_profit"] / df["mrr"].clip(lower=1e-9)) * 100.0

    return df
