# How to publish the trading dashboard to the public web

This records what was done to make **TradingDashboard - Public** viewable without signing in, so it can be repeated for another report.

**Public link:** https://app.powerbi.com/view?r=eyJrIjoiNDI0MGFmYWItMzRiMi00Njc5LTg2Y2UtZjdhMzcwYmJkMGUyIiwidCI6ImQxZmYwZmFmLTA5ZWItNDJjZi04MzEzLTA3MzNiM2Y3MDdkNyIsImMiOjR9

## Why a copy was needed
Power BI's **Publish to web** rejects the Direct Lake model (`sm_trading_gold`). It reads OneLake with the signed-in user's identity, and that is blocked for public reports. The fix is a second model in **Import** mode that reads the same tables, with the report cloned onto it. The original model and report are left unchanged for private work.

## Steps

### 1. Tenant settings (Fabric admin)
- *Allow users to create new embed codes*: on
- *Publish to web*: enabled
- *Block Public Internet Access*: off

### 2. Build the Import model
Run `fabric/notebooks/nb_build_import_model.py` in a Fabric notebook (Trading-Dev workspace, Lakehouse attached as needed):
1. Reads the Direct Lake model's definition (`labs.get_semantic_model_bim`).
2. Replaces each `directLake` table partition with an Import partition: `Sql.Database(<SQL endpoint>, "TradingLakehouse")`, then the table's schema and name.
3. Removes the Direct Lake shared expression.
4. Creates `sm_trading_gold_import` with `labs.create_semantic_model_from_bim`.

Result: 9 tables, 121 measures, 8 relationships.

### 3. Connect the data source
The new model's default is *Default: Single Sign-On*, which can't refresh and also blocks Publish to web.
1. Workspace → `sm_trading_gold_import` → Settings → Gateway and cloud connections.
2. Under *Maps to*, choose **Create a connection**: type *Cloud*, connection type *SQL Server*, the lakehouse SQL endpoint server, database `tradinglakehouse`, authentication **OAuth 2.0**, and sign in with your account. Create it.
3. Back on the model's settings, set *Maps to* to that connection and Apply.

### 4. Refresh the model
Run a full refresh (Settings → Refresh, or `labs.refresh_semantic_model`). It must finish without errors.

### 5. Clone the report onto the Import model
Use the Power BI REST API `Reports/Clone` (`targetModelId` = the Import model's ID). This created **TradingDashboard - Public**, bound to `sm_trading_gold_import`.

### 6. Add the pages
Duplicate pages in the public report, then rebind each visual to the matching measure from `dax/`. The page layouts are in `docs/report-build-guide.md`. The measures must also be loaded into the Import model (DAX query view, paste `dax/_all-measures.dax`, Update model).

### 7. Publish to web
In the report: **File → Embed report → Publish to web (public)** → Continue → Publish. Copy the link labelled *Link you can send in email*.

## Things to know
- **Anyone with the link can see all data in the Import model.** Use it only for data you are happy to share.
- **Changes are not instant.** Publish to web caches the report; new pages can take up to an hour to appear.
- **The public copy only updates on refresh.** Set a scheduled refresh on `sm_trading_gold_import`, otherwise numbers go stale.
- **Repeat for other reports.** FinanceDashboard uses the same steps (Finance-sm → Import copy → clone → connect → refresh → publish). It has not been published.

## Related files
- `fabric/notebooks/nb_build_import_model.py`: the model-copy notebook.
- `dax/`: the measure library, by page.
- `docs/report-build-guide.md`: visual slots and measures for each page.
- `docs/publish-to-web.md`: short summary of the approach.
- `dashboard/screenshots/`: screenshots of pages 1–3.
