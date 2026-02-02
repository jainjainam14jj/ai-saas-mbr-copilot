from __future__ import annotations

import pandas as pd


def build_memo(df: pd.DataFrame, bridge: pd.DataFrame) -> str:
    # Use last month as the headline
    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else last

    mrr_delta = last["mrr"] - prev["mrr"]
    gm_delta = last["gross_margin_pct"] - prev["gross_margin_pct"]

    top_line = (
        f"## Monthly Business Review — {last['month']}\n\n"
        f"**Headline:** MRR ended at **${last['mrr']:,.0f}** (MoM change **${mrr_delta:,.0f}**). "
        f"Gross margin finished at **{last['gross_margin_pct']:.1f}%** (MoM change **{gm_delta:+.1f} pts**).\n\n"
    )

    drivers = "### What drove the change?\n"
    if len(bridge) > 0:
        b = bridge.iloc[-1]
        drivers += (
            f"- Seat MRR change: **${b['delta_seat']:,.0f}**\n"
            f"- Usage MRR change: **${b['delta_usage']:,.0f}**\n"
        )

    ops = (
        "\n### Focus areas\n"
        "- Improve expansion (NRR) via deeper workflow adoption and credits-driven value.\n"
        "- Track inference efficiency (cost per 1k tokens) and push model/infra optimizations.\n"
        "- Maintain sales efficiency: watch payback proxy via margin and growth mix.\n"
    )

    return top_line + drivers + ops
