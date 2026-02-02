from __future__ import annotations

import pandas as pd


def add_opex_and_runway(df: pd.DataFrame, opex: pd.DataFrame, cash: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    out = df.merge(opex, on="month", how="left")

    defaults = cfg.get("default_opex_monthly", {})
    out["rnd"] = out["rnd"].fillna(float(defaults.get("rnd", 0)))
    out["sales_marketing"] = out["sales_marketing"].fillna(float(defaults.get("sales_marketing", 0)))
    out["g_and_a"] = out["g_and_a"].fillna(float(defaults.get("g_and_a", 0)))
    out["opex_total"] = out[["rnd", "sales_marketing", "g_and_a"]].sum(axis=1)

    out["ebitda"] = out["gross_profit"] - out["opex_total"]
    out["ebitda_margin_pct"] = (out["ebitda"] / out["mrr"].clip(lower=1e-9)) * 100.0

    # Runway: simple cash balance = starting_cash + cumulative EBITDA
    start_cash = float(cfg.get("starting_cash", 0.0))
    if "starting_cash" in cash.columns and len(cash) > 0:
        start_cash = float(cash.iloc[0]["starting_cash"])

    out["cash_balance"] = start_cash + out["ebitda"].cumsum()
    out["burn"] = (-out["ebitda"]).clip(lower=0)

    return out
