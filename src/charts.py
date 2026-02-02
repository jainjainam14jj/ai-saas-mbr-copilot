from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def save_charts(df: pd.DataFrame, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    # MRR + GM
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(df["month"], df["mrr"], label="MRR", linewidth=2)
    ax1.set_title("MRR")
    ax1.set_ylabel("$")
    ax1.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_dir / "mrr.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["month"], df["gross_margin_pct"], label="GM%", linewidth=2, color="#1b9e77")
    ax.set_title("Gross Margin %")
    ax.set_ylabel("%")
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_dir / "gross_margin.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.stackplot(df["month"], df["seat_mrr"], df["usage_mrr"], labels=["Seat", "Usage"], alpha=0.9)
    ax.set_title("MRR Mix")
    ax.set_ylabel("$")
    ax.legend(loc="upper left")
    ax.grid(True, alpha=0.2)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_dir / "mrr_mix.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["month"], df["cash_balance"], linewidth=2, color="#2a6fdb")
    ax.set_title("Cash Balance (Runway)")
    ax.set_ylabel("$")
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_dir / "runway.png", dpi=200)
    plt.close(fig)
