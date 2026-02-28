from __future__ import annotations

import pandas as pd


def mrr_bridge_customer(customer_rev: pd.DataFrame) -> pd.DataFrame:
    """MRR bridge using customer-level MRR movements.

    For each month t vs t-1:
      - New: customers present in t but not t-1
      - Churn: customers present in t-1 but not t
      - Expansion: customers present both with MRR up
      - Contraction: customers present both with MRR down

    Returns month-level bridge table.
    """

    df = customer_rev[["month", "customer_id", "mrr", "seat_mrr", "usage_mrr"]].copy()
    df["month"] = df["month"].astype(str)

    months = sorted(df["month"].unique())
    rows = []

    prev = None
    for m in months:
        cur = df[df["month"] == m].set_index("customer_id")

        if prev is None:
            prev = cur
            continue

        prev_ids = set(prev.index)
        cur_ids = set(cur.index)

        new_ids = cur_ids - prev_ids
        churn_ids = prev_ids - cur_ids
        common_ids = cur_ids & prev_ids

        new_mrr = float(cur.loc[list(new_ids), "mrr"].sum()) if new_ids else 0.0
        churn_mrr = float(prev.loc[list(churn_ids), "mrr"].sum()) if churn_ids else 0.0

        delta_common = (cur.loc[list(common_ids), "mrr"] - prev.loc[list(common_ids), "mrr"]) if common_ids else pd.Series(dtype=float)
        expansion_mrr = float(delta_common[delta_common > 0].sum()) if len(delta_common) else 0.0
        contraction_mrr = float((-delta_common[delta_common < 0]).sum()) if len(delta_common) else 0.0

        prev_mrr = float(prev["mrr"].sum())
        end_mrr = float(cur["mrr"].sum())

        rows.append(
            {
                "month": m,
                "prev_mrr": prev_mrr,
                "end_mrr": end_mrr,
                "new_mrr": new_mrr,
                "expansion_mrr": expansion_mrr,
                "contraction_mrr": contraction_mrr,
                "churn_mrr": churn_mrr,
                "net_change": end_mrr - prev_mrr,
            }
        )

        prev = cur

    return pd.DataFrame(rows)


def gm_bridge(df: pd.DataFrame) -> pd.DataFrame:
    d = df.sort_values("month").copy()
    d["prev_gm"] = d["gross_margin_pct"].shift(1)
    d["delta_gm"] = d["gross_margin_pct"] - d["prev_gm"]
    out = d[["month", "prev_gm", "gross_margin_pct", "delta_gm"]].dropna()
    return out
