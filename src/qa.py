from __future__ import annotations

import pandas as pd


def qa(df: pd.DataFrame) -> list[str]:
    issues: list[str] = []

    if (df["customers"] < 0).any():
        issues.append("ERROR: Negative customers.")

    for c in ["mrr", "seat_mrr", "usage_mrr"]:
        if c in df.columns and (df[c] < 0).any():
            issues.append("ERROR: Negative MRR values.")

    # Mix check
    if all(c in df.columns for c in ["seat_mrr", "usage_mrr", "mrr"]):
        diff = (df["seat_mrr"] + df["usage_mrr"] - df["mrr"]).abs().max()
        if diff > 1e-6:
            issues.append(f"ERROR: seat_mrr + usage_mrr != mrr (max diff {diff}).")

    if not issues:
        issues.append("OK: No issues found.")
    return issues
