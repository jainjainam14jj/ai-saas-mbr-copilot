from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

import yaml
import pandas as pd

from src.ingest import load_inputs
from src.kpis import build_monthly_kpis
from src.cogs import add_cogs
from src.runway import add_opex_and_runway
from src.bridges import mrr_bridge, gm_bridge
from src.charts import save_charts
from src.narrative import build_memo
from src.qa import qa


def run(cmd: list[str], cwd: Path) -> None:
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{p.stdout}\n{p.stderr}")


def main() -> None:
    root = Path(__file__).resolve().parent
    cfg = yaml.safe_load((root / "inputs" / "assumptions.yaml").read_text(encoding="utf-8"))

    scenarios = list((cfg.get("scenarios") or {}).keys()) or ["base"]

    # Ensure docs exists
    docs = root / "docs"
    if docs.exists():
        shutil.rmtree(docs)
    (docs / "charts").mkdir(parents=True, exist_ok=True)

    # Load inputs
    inputs = load_inputs(root)

    # Assumptions summary (published)
    assumptions_summary = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "horizon": {"start_month": cfg.get("start_month"), "end_month": cfg.get("end_month")},
        "scenarios": cfg.get("scenarios", {}),
        "base_inputs": {
            "new_customers_per_month": cfg.get("new_customers_per_month"),
            "logo_churn_rate_monthly_0_3": cfg.get("logo_churn_rate_monthly_0_3"),
            "logo_churn_rate_monthly_4_plus": cfg.get("logo_churn_rate_monthly_4_plus"),
            "seat_expansion_rate_monthly_0_3": cfg.get("seat_expansion_rate_monthly_0_3"),
            "seat_expansion_rate_monthly_4_plus": cfg.get("seat_expansion_rate_monthly_4_plus"),
            "usage_expansion_multiplier": cfg.get("usage_expansion_multiplier"),
        },
    }
    (docs / "assumptions_summary.json").write_text(json.dumps(assumptions_summary, indent=2), encoding="utf-8")

    for scenario in scenarios:
        sc = cfg["scenarios"][scenario]

        # For v1 we apply scenario multipliers only to costs + narrative; full cohort scenario engine can be v2.
        # (We already have cohort engine in Clay project; here we focus on MBR automation.)
        kpis = build_monthly_kpis(inputs["subs"], inputs["usage"])
        kpis["scenario"] = scenario

        kpis = add_cogs(kpis, inputs["cogs_ai"], sc | cfg)
        kpis = add_opex_and_runway(kpis, inputs["opex"], inputs["cash"], cfg)

        bridge = mrr_bridge(kpis)
        gmbr = gm_bridge(kpis)
        memo = build_memo(kpis, bridge)
        issues = qa(kpis)

        # Write CSVs
        kpis.to_csv(docs / f"mbr_kpis_{scenario}.csv", index=False)
        bridge.to_csv(docs / f"mrr_bridge_{scenario}.csv", index=False)
        gmbr.to_csv(docs / f"gm_bridge_{scenario}.csv", index=False)

        # Runway
        kpis[["month", "cash_balance", "burn", "ebitda"]].to_csv(docs / f"runway_{scenario}.csv", index=False)

        # Memo + QA
        (docs / f"mbr_memo_{scenario}.md").write_text(memo, encoding="utf-8")
        (docs / f"qa_report_{scenario}.md").write_text("\n".join(f"- {x}" for x in issues) + "\n", encoding="utf-8")

        # Charts
        save_charts(kpis, docs / "charts" / scenario)

    # Index
    (docs / "index.html").write_text(
        """<!doctype html><html><head><meta charset=\"utf-8\" /><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
<title>AI SaaS MBR Copilot — Outputs</title>
<style>body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial;max-width:900px;margin:40px auto;padding:0 16px;}code{background:#f4f4f4;padding:2px 6px;border-radius:6px;}</style>
</head><body>
<h1>AI SaaS MBR Copilot — Static Outputs</h1>
<p>Published for Lovable dashboard via GitHub Pages.</p>
<ul><li><a href=\"assumptions_summary.json\">assumptions_summary.json</a></li></ul>
</body></html>""",
        encoding="utf-8",
    )

    # Git commit + push
    run(["git", "add", "docs", "inputs/assumptions.yaml", "publish_mbr.py", "src", "scripts", "README.md", "requirements.txt", ".gitignore"], cwd=root)
    try:
        run(["git", "commit", "-m", "Publish MBR pack"], cwd=root)
    except RuntimeError as e:
        if "nothing to commit" not in str(e):
            raise

    run(["git", "push"], cwd=root)

    print("Published. GitHub Pages will update shortly.")


if __name__ == "__main__":
    main()
