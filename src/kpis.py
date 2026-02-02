from __future__ import annotations

import pandas as pd


def build_monthly_kpis(subs: pd.DataFrame, usage: pd.DataFrame) -> pd.DataFrame:
    # Aggregate MRR from subscriptions
    mrr = subs.groupby("month", as_index=False).agg(
        customers=("customer_id", "nunique"),
        seats=("seats", "sum"),
        seat_mrr=("mrr", "sum"),
    )

    # Aggregate usage revenue + tokens
    u = usage.groupby("month", as_index=False).agg(
        tokens_in=("tokens_in", "sum"),
        tokens_out=("tokens_out", "sum"),
        api_calls=("api_calls", "sum"),
        usage_mrr=("usage_revenue", "sum"),
    )

    df = mrr.merge(u, on="month", how="left").fillna(0)
    df["mrr"] = df["seat_mrr"] + df["usage_mrr"]
    df["arr"] = df["mrr"] * 12.0
    df["arpc_mrr"] = df["mrr"] / df["customers"].clip(lower=1)
    df["usage_share_pct"] = (df["usage_mrr"] / df["mrr"].clip(lower=1e-9)) * 100.0
    return df
