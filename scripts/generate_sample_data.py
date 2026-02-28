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
    rng = np.random.default_rng(11)

    # Synthetic customer base
    n0 = 220
    customer_ids = [f"ACCT{str(i).zfill(4)}" for i in range(1, 4000)]
    active = set(customer_ids[:n0])

    subs_rows = []
    usage_rows = []

    seat_px = 20.0

    for t, m in enumerate(months):
        # new customers
        new_n = 35
        new = customer_ids[n0 + t * new_n : n0 + (t + 1) * new_n]
        for cid in new:
            active.add(cid)

        # churn
        churn_rate = 0.028 if t < 4 else 0.018
        churn_n = int(len(active) * churn_rate)
        churned = set(rng.choice(list(active), size=max(churn_n, 0), replace=False)) if churn_n else set()
        active -= churned

        for cid in list(active):
            # dev seats (subscription component)
            dev_seats = max(1, int(rng.normal(3.0, 1.2)))
            seat_mrr = dev_seats * seat_px

            # usage units (Vercel-ish)
            edge_m = max(0.1, rng.lognormal(mean=2.2, sigma=0.6))  # millions
            data_gb = max(5.0, rng.lognormal(mean=5.7, sigma=0.5))  # GB
            build_min = max(20.0, rng.lognormal(mean=4.8, sigma=0.6))  # minutes

            subs_rows.append(
                {
                    "month": m.strftime("%Y-%m"),
                    "customer_id": cid,
                    "plan": "pro",
                    "dev_seats": dev_seats,
                    "seat_mrr": seat_mrr,
                }
            )

            usage_rows.append(
                {
                    "month": m.strftime("%Y-%m"),
                    "customer_id": cid,
                    "edge_requests_millions": float(edge_m),
                    "fast_data_transfer_gb": float(data_gb),
                    "build_minutes": float(build_min),
                }
            )

    pd.DataFrame(subs_rows).to_csv(raw / "subscriptions_monthly.csv", index=False)
    pd.DataFrame(usage_rows).to_csv(raw / "usage_monthly.csv", index=False)

    # Infra unit costs (illustrative)
    cogs = pd.DataFrame(
        {
            "month": [m.strftime("%Y-%m") for m in months],
            "cost_per_gb": np.linspace(0.020, 0.014, len(months)),
            "cost_per_1m_edge": np.linspace(0.35, 0.25, len(months)),
            "cost_per_build_min": np.linspace(0.004, 0.003, len(months)),
            "infra_fixed_cost": np.linspace(180_000, 260_000, len(months)),
        }
    )
    cogs.to_csv(raw / "cogs_ai_monthly.csv", index=False)

    # Opex
    opex = pd.DataFrame(
        {
            "month": [m.strftime("%Y-%m") for m in months],
            "rnd": np.linspace(260_000, 420_000, len(months)),
            "sales_marketing": np.linspace(320_000, 520_000, len(months)),
            "g_and_a": np.linspace(140_000, 210_000, len(months)),
        }
    )
    opex.to_csv(raw / "opex_monthly.csv", index=False)

    # Cash
    pd.DataFrame({"month": [months[0].strftime("%Y-%m")], "starting_cash": [3_500_000]}).to_csv(
        raw / "cash_monthly.csv", index=False
    )

    print("Wrote sample CSVs to", raw)


if __name__ == "__main__":
    main()
