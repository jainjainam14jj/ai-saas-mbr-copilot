from __future__ import annotations

import pandas as pd


def add_cogs(kpis: pd.DataFrame, cogs_ai: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Add infra COGS (variable by unit + fixed) and gross margin.

    We reuse cogs_ai_monthly.csv but interpret it as infra unit costs:
      - cost_per_gb
      - cost_per_1m_edge
      - cost_per_build_min
      - infra_fixed_cost
    """

    df = kpis.merge(cogs_ai, on="month", how="left").fillna(0)

    mult = float(cfg.get("infra_unit_cost_mult", 1.0))
    df["cost_per_gb"] = df["cost_per_gb"] * mult
    df["cost_per_1m_edge"] = df["cost_per_1m_edge"] * mult
    df["cost_per_build_min"] = df["cost_per_build_min"] * mult

    df["infra_variable_cogs"] = (
        df["fast_data_transfer_gb"] * df["cost_per_gb"]
        + df["edge_requests_millions"] * df["cost_per_1m_edge"]
        + df["build_minutes"] * df["cost_per_build_min"]
    )

    df["infra_cogs"] = df["infra_variable_cogs"] + df["infra_fixed_cost"]

    other_pct = float(cfg.get("cogs_other_percent_of_revenue", 0.0))
    df["other_cogs"] = df["mrr"] * other_pct
    df["total_cogs"] = df["infra_cogs"] + df["other_cogs"]

    df["gross_profit"] = df["mrr"] - df["total_cogs"]
    df["gross_margin_pct"] = (df["gross_profit"] / df["mrr"].clip(lower=1e-9)) * 100.0

    return df
