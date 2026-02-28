from __future__ import annotations

import pandas as pd


def apply_usage_pricing(usage: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Compute usage revenue per customer-month using included + overage pricing.

    Expected columns in usage:
      month, customer_id, edge_requests_millions, fast_data_transfer_gb, build_minutes

    Returns a copy with:
      usage_mrr, edge_revenue, data_revenue, build_revenue, plus overage volumes.

    Notes:
    - Included amounts are modeled per account/month.
    - This is illustrative; actual enterprise contracts can differ.
    """

    df = usage.copy()

    inc_edge = float(cfg.get("edge_requests_included_millions_per_account", 0.0))
    px_edge = float(cfg.get("edge_requests_overage_per_million_usd", 0.0))

    inc_gb = float(cfg.get("fast_data_transfer_included_gb_per_account", 0.0))
    px_gb = float(cfg.get("fast_data_transfer_overage_per_gb_usd", 0.0))

    inc_build = float(cfg.get("build_minutes_included_per_account", 0.0))
    px_build = float(cfg.get("build_minutes_overage_per_min_usd", 0.0))

    df["edge_overage_millions"] = (df["edge_requests_millions"] - inc_edge).clip(lower=0)
    df["data_overage_gb"] = (df["fast_data_transfer_gb"] - inc_gb).clip(lower=0)
    df["build_overage_minutes"] = (df["build_minutes"] - inc_build).clip(lower=0)

    df["edge_revenue"] = df["edge_overage_millions"] * px_edge
    df["data_revenue"] = df["data_overage_gb"] * px_gb
    df["build_revenue"] = df["build_overage_minutes"] * px_build

    df["usage_mrr"] = df[["edge_revenue", "data_revenue", "build_revenue"]].sum(axis=1)

    return df
