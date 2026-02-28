from __future__ import annotations

import pandas as pd

from src.pricing import apply_usage_pricing


def build_customer_revenue(subs: pd.DataFrame, usage: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Build customer-month revenue table (seat + usage) for bridges and KPIs."""

    # Seat revenue: dev seats * $/seat
    seat_px = float(cfg.get("seat_price_dev_monthly", 0.0))

    subs2 = subs.copy()
    if "dev_seats" not in subs2.columns:
        # fallback: treat `seats` as dev seats
        subs2["dev_seats"] = subs2.get("seats", 0)

    subs2["seat_mrr"] = subs2["dev_seats"].fillna(0) * seat_px

    # Usage revenue (included + overage)
    usage2 = apply_usage_pricing(usage, cfg)

    # Merge to customer-month
    out = subs2[["month", "customer_id", "dev_seats", "seat_mrr"]].merge(
        usage2[[
            "month",
            "customer_id",
            "edge_requests_millions",
            "fast_data_transfer_gb",
            "build_minutes",
            "edge_overage_millions",
            "data_overage_gb",
            "build_overage_minutes",
            "edge_revenue",
            "data_revenue",
            "build_revenue",
            "usage_mrr",
        ]],
        on=["month", "customer_id"],
        how="left",
    ).fillna(0)

    out["mrr"] = out["seat_mrr"] + out["usage_mrr"]
    return out


def build_monthly_kpis(customer_rev: pd.DataFrame) -> pd.DataFrame:
    """Aggregate monthly KPIs."""

    df = customer_rev.groupby("month", as_index=False).agg(
        customers=("customer_id", "nunique"),
        dev_seats=("dev_seats", "sum"),
        seat_mrr=("seat_mrr", "sum"),
        usage_mrr=("usage_mrr", "sum"),
        edge_requests_millions=("edge_requests_millions", "sum"),
        fast_data_transfer_gb=("fast_data_transfer_gb", "sum"),
        build_minutes=("build_minutes", "sum"),
        edge_revenue=("edge_revenue", "sum"),
        data_revenue=("data_revenue", "sum"),
        build_revenue=("build_revenue", "sum"),
    )

    df["mrr"] = df["seat_mrr"] + df["usage_mrr"]
    df["arr"] = df["mrr"] * 12.0
    df["arpc_mrr"] = df["mrr"] / df["customers"].clip(lower=1)
    df["usage_share_pct"] = (df["usage_mrr"] / df["mrr"].clip(lower=1e-9)) * 100.0

    # Unit economics helpers
    df["rev_per_gb"] = df["data_revenue"] / df["fast_data_transfer_gb"].clip(lower=1e-9)
    df["rev_per_1m_edge"] = df["edge_revenue"] / df["edge_requests_millions"].clip(lower=1e-9)
    df["rev_per_build_min"] = df["build_revenue"] / df["build_minutes"].clip(lower=1e-9)

    return df
