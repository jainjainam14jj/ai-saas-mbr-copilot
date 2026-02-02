from __future__ import annotations

import pandas as pd
import numpy as np


def apply_scenario_to_kpis(base: pd.DataFrame, sc: dict, cfg: dict) -> pd.DataFrame:
    """Create a scenario-adjusted KPI series from a base monthly KPI series.

    Goal: make scenario toggles visibly and intuitively change trajectories without
    requiring a full CRM-style cohort simulation.

    Approach:
    - Take month-over-month deltas from base.
    - Scale positive deltas by (new_logo_mult * expansion_mult).
    - Scale negative deltas by churn_mult.

    This produces CFO-intuitive upside/downside: growth accelerates or slows;
    contractions get better/worse.

    Note: cost per 1k tokens is handled downstream in add_cogs via cost_per_1k_tokens_mult.
    """

    df = base.sort_values("month").reset_index(drop=True).copy()

    growth_mult = float(sc.get("new_logo_mult", 1.0)) * float(sc.get("expansion_mult", 1.0))
    usage_growth_mult = float(sc.get("new_logo_mult", 1.0)) * float(sc.get("expansion_mult", 1.0)) * float(
        cfg.get("usage_expansion_multiplier", 1.0)
    )
    shrink_mult = float(sc.get("churn_mult", 1.0))

    # Which columns to adjust (keep month, scenario separately)
    adjust_cols = [
        "customers",
        "seats",
        "seat_mrr",
        "usage_mrr",
        "tokens_in",
        "tokens_out",
        "api_calls",
    ]

    for col in adjust_cols:
        if col not in df.columns:
            continue

        base_vals = df[col].astype(float).to_numpy()
        out = np.zeros_like(base_vals)
        out[0] = base_vals[0]

        for t in range(1, len(base_vals)):
            delta = base_vals[t] - base_vals[t - 1]

            if col in {"usage_mrr", "tokens_in", "tokens_out", "api_calls"}:
                pos_mult = usage_growth_mult
            else:
                pos_mult = growth_mult

            delta_adj = delta * (pos_mult if delta >= 0 else shrink_mult)
            out[t] = max(out[t - 1] + delta_adj, 0.0)

        df[col] = out

    # Recompute derived fields
    df["mrr"] = df["seat_mrr"] + df["usage_mrr"]
    df["arr"] = df["mrr"] * 12.0
    df["arpc_mrr"] = df["mrr"] / df["customers"].clip(lower=1)
    df["usage_share_pct"] = (df["usage_mrr"] / df["mrr"].clip(lower=1e-9)) * 100.0

    return df
