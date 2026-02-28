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
        # Support both old bridge (delta_seat/delta_usage) and new customer bridge
        if "new_mrr" in b.index:
            drivers += (
                f"- New: **+${float(b.get('new_mrr', 0.0)):,.0f}**\n"
                f"- Expansion: **+${float(b.get('expansion_mrr', 0.0)):,.0f}**\n"
                f"- Contraction: **-${float(b.get('contraction_mrr', 0.0)):,.0f}**\n"
                f"- Churn: **-${float(b.get('churn_mrr', 0.0)):,.0f}**\n"
            )
        else:
            drivers += (
                f"- Seat MRR change: **${float(b.get('delta_seat', 0.0)):,.0f}**\n"
                f"- Usage MRR change: **${float(b.get('delta_usage', 0.0)):,.0f}**\n"
            )

    ops = (
        "\n### Focus areas\n"
        "- Monitor retention and expansion (NRR) and identify churn/downsells by cohort.\n"
        "- Track unit economics: $/GB, $/1M edge requests, and $/build minute vs unit costs.\n"
        "- Watch GM drivers: usage mix shift + infra unit cost trends + fixed cost absorption.\n"
    )

    return top_line + drivers + ops
