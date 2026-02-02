from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd


def month_range(start: str, end: str) -> pd.DatetimeIndex:
    return pd.date_range(pd.to_datetime(start + "-01"), pd.to_datetime(end + "-01"), freq="MS")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    raw = root / "inputs" / "raw"
    raw.mkdir(parents=True, exist_ok=True)

    months = month_range("2026-01", "2028-12")
    rng = np.random.default_rng(7)

    # Create synthetic customer base
    n0 = 300
    customer_ids = [f"C{str(i).zfill(4)}" for i in range(1, 2000)]
    active = set(customer_ids[:n0])

    sub_rows = []
    usage_rows = []

    price_seat = 99
    price_1k_tokens = 0.60

    for t, m in enumerate(months):
        # new customers
        new_n = 40
        new = customer_ids[n0 + t * new_n : n0 + (t + 1) * new_n]
        for cid in new:
            active.add(cid)

        # churn some
        churn_rate = 0.03 if t < 4 else 0.02
        churn_n = int(len(active) * churn_rate)
        churned = set(rng.choice(list(active), size=max(churn_n, 0), replace=False)) if churn_n else set()
        active -= churned

        for cid in list(active):
            # seats and mrr (small variation)
            seats = max(1, int(rng.normal(4.0, 1.0)))
            mrr = seats * price_seat

            # token usage (high variance)
            tokens_in = max(0, int(rng.normal(600_000, 200_000)))
            tokens_out = max(0, int(rng.normal(500_000, 180_000)))
            api_calls = max(0, int(rng.normal(120, 50)))

            sub_rows.append({
                "month": m.strftime("%Y-%m"),
                "customer_id": cid,
                "plan": "pro",
                "seats": seats,
                "mrr": mrr,
            })

            usage_rows.append({
                "month": m.strftime("%Y-%m"),
                "customer_id": cid,
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "api_calls": api_calls,
                "usage_revenue": ((tokens_in + tokens_out) / 1000.0) * price_1k_tokens,
            })

    pd.DataFrame(sub_rows).to_csv(raw / "subscriptions_monthly.csv", index=False)
    pd.DataFrame(usage_rows).to_csv(raw / "usage_monthly.csv", index=False)

    # COGS AI
    cogs_ai = pd.DataFrame({
        "month": [m.strftime("%Y-%m") for m in months],
        "cost_per_1k_tokens": np.linspace(0.25, 0.18, len(months)),
        "infra_fixed_cost": np.linspace(40_000, 70_000, len(months)),
    })
    cogs_ai.to_csv(raw / "cogs_ai_monthly.csv", index=False)

    # Opex
    opex = pd.DataFrame({
        "month": [m.strftime("%Y-%m") for m in months],
        "rnd": np.linspace(220_000, 320_000, len(months)),
        "sales_marketing": np.linspace(260_000, 360_000, len(months)),
        "g_and_a": np.linspace(110_000, 150_000, len(months)),
    })
    opex.to_csv(raw / "opex_monthly.csv", index=False)

    # Cash
    pd.DataFrame({"month": [months[0].strftime("%Y-%m")], "starting_cash": [2_500_000]}).to_csv(
        raw / "cash_monthly.csv", index=False
    )

    print("Wrote sample CSVs to", raw)


if __name__ == "__main__":
    main()
