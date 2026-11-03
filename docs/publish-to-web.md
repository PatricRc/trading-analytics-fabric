# Publish to web

**Live report:** https://app.powerbi.com/view?r=eyJrIjoiNDI0MGFmYWItMzRiMi00Njc5LTg2Y2UtZjdhMzcwYmJkMGUyIiwidCI6ImQxZmYwZmFmLTA5ZWItNDJjZi04MzEzLTA3MzNiM2Y3MDdkNyIsImMiOjR9

Publish to web rejects Direct Lake models ("report is not eligible"), because they read OneLake with the viewer's identity (SSO). The public version therefore runs on an Import-mode copy:

| Item | Mode | Purpose |
|---|---|---|
| `sm_trading_gold` + `TradingDashboard` | Direct Lake | development, always current |
| `sm_trading_gold_import` + `TradingDashboard - Public` | Import | Publish to web |

## How it was built
1. `fabric/notebooks/nb_build_import_model.py` (semantic-link-labs) reads the Direct Lake model's BIM, swaps every `directLake` entity partition for an Import partition (`Sql.Database(<SQL endpoint>, "TradingLakehouse")`), and creates `sm_trading_gold_import`. Same 9 tables, 121 measures, 8 relationships.
2. The report was cloned onto it with the Power BI REST `Reports/Clone` API (`targetModelId`).
3. The model's SQL data source is mapped to the cloud connection **TradingLakehouse SQL endpoint (OAuth)** instead of *Default: Single Sign-On* (SSO is also blocked by Publish to web).
4. Full refresh, then File → Embed report → Publish to web (public).

## Keeping it current
The Import copy only changes when it refreshes. Add a scheduled refresh on `sm_trading_gold_import` (Settings → Refresh). When `sm_trading_gold` gains measures or tables, re-run the notebook into a new name or update the copy, and re-clone if the report changes.

The same recipe applies to FinanceDashboard / Finance-sm.
