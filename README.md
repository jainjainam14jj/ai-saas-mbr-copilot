# AI SaaS MBR Copilot (FP&A Automation)

**Goal:** Drop in exports + update assumptions → run **one command** → publish a CFO-ready Monthly Business Review pack.

## What it generates (GitHub Pages `/docs`)
- `docs/mbr_kpis_<scenario>.csv`
- `docs/mrr_bridge_<scenario>.csv`
- `docs/gm_bridge_<scenario>.csv`
- `docs/cohort_nrr_<scenario>.csv`
- `docs/runway_<scenario>.csv`
- `docs/mbr_memo_<scenario>.md`
- `docs/qa_report_<scenario>.md`
- `docs/charts/<scenario>/*.png`

## Quickstart
```bash
cd ai-saas-mbr-copilot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# (Optional) generate realistic sample inputs
python scripts/generate_sample_data.py

# Build + publish to GitHub Pages
python publish_mbr.py
```

## Inputs
- `inputs/assumptions.yaml`
- `inputs/raw/*.csv`

## Notes
This is a portfolio project designed to demonstrate Strategic Finance + FP&A automation in an AI SaaS context.
