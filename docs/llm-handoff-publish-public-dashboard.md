# Handoff: publish a Power BI dashboard to the public web

**Audience:** an LLM agent (or a person) that must publish a second Power BI report, FinanceDashboard, to Publish to web.
**Reference result:** TradingDashboard - Public. Public link: https://app.powerbi.com/view?r=eyJrIjoiNDI0MGFmYWItMzRiMi00Njc5LTg2Y2UtZjdhMzcwYmJkMGUyIiwidCI6ImQxZmYwZmFmLTA5ZWItNDJjZi04MzEzLTA3MzNiM2Y3MDdkNyIsImMiOjR9

## 0. Rules before you start
- **Publishing makes all data in the model viewable by anyone with the link.** Do not publish, create an embed code, or share a link until the user explicitly says "publish FinanceDashboard" in this conversation. Preparing the copy is fine; publishing is not.
- Do not write, store or print credentials. The OAuth sign-in is done by the user in a browser popup.
- Keep the original Direct Lake model and report untouched. Everything public goes into a new copy.
- Commit and push only what the user asks for.

## 1. Why a copy is needed
Publish to web rejects a report whose model is:
- Direct Lake (reads OneLake with the viewer's identity),
- DirectQuery or a live connection,
- on single sign-on to the data source, or
- row-level secured.

Power BI's error: "the report is not eligible for use with Publish to web". The fix is a second semantic model in **Import** mode with the same tables, measures and relationships, and the report cloned onto it.

## 2. Check the source first
Find the source model (`Finance-sm`, Finance Reporting workspace, id `9599c6dc-0b60-4c23-9ef8-1633f2279e67`, FinanceDashboard report id `d7c41415-b920-47c3-b096-e0cd80b871a2`; confirm these in the workspace).
- Storage mode and source: Settings → data source. If it is Import already, the Import copy is optional, but the tenant and SSO checks below still apply.
- Confirm there are no RLS roles (Security). RLS blocks publishing.
- Count the measures (expected 80) and relationships. The copy must keep them.

## 3. Tenant settings (Fabric admin, already done for this tenant)
- Allow users to create new embed codes: On
- Publish to web: enabled
- Block Public Internet Access: Off

## 4. Build the Import copy
Reference notebook: `fabric/notebooks/nb_build_import_model.py` (in this repo). Copy it into a new notebook in the **Finance Reporting** workspace (or the workspace where the source model lives) and change these values:
- `WS_ID`: the workspace id of the source model.
- `LH_ID`: the lakehouse the source model reads. If the source has no lakehouse (for example an Import model), skip the Import conversion and clone the report onto a copy made in Power BI Desktop instead.
- `SRC`: the source model name (`Finance-sm`).
- `DST`: the new name (`Finance-sm-import`).

What the notebook does:
1. Installs `semantic-link-labs` (`%pip install -q semantic-link-labs`). Restart the kernel if prompted.
2. Reads the model definition (`labs.get_semantic_model_bim`).
3. Replaces each partition whose mode is `directLake` (or whose source type is `entity`) with an Import partition: `Sql.Database("<SQL endpoint>", "<database>")` then `Data{[Schema=..., Item=...]}`.
4. Removes the `DatabaseQuery` expression and sets the model to Import.
5. Creates the model with `labs.create_semantic_model_from_bim`.

Expect the same number of tables, measures and relationships as the source. Check the printed counts.

## 5. Connect the data source (user step)
A new model maps to *Default: Single Sign-On*. Refresh fails with: "We cannot refresh this semantic model because this semantic model uses a default data connection without explicit connection credentials." Publish to web also blocks SSO.
1. Open `DST` → Settings → Gateway and cloud connections.
2. *Maps to* → **Create a connection**. Fill in: Connection name, Connection type *SQL Server*, the server and database that the notebook printed, Authentication method **OAuth 2.0**.
3. Click **Edit credentials**. A Microsoft sign-in popup opens in a separate window. The user picks their account and signs in.
4. **Click Create immediately after signing in.** If the panel stays open for a long time, the token expires and Create fails with "It looks like the refresh token expired".
5. Back on the model's settings, set *Maps to* to the new connection and click Apply.

An agent cannot complete the popup. Ask the user to do steps 3–4 and wait for confirmation.

## 6. Refresh
Settings → Refresh → Refresh now, or run `labs.refresh_semantic_model(dataset=DST, workspace=WS_ID)` in the notebook. Expect the message "Refresh 'full' … is complete". Check that it finishes without errors before going on.

## 7. Clone the report onto the copy
`labs.report.clone_report` was not available in this environment. Use the REST API from the notebook:
```python
pbi = fabric.PowerBIRestClient()
pbi.post(f"v1.0/myorg/groups/{WS_ID}/reports/{REPORT_ID}/Clone",
         json={"name": "FinanceDashboard - Public", "targetWorkspaceId": WS_ID, "targetModelId": DST_MODEL_ID})
```
Get `DST_MODEL_ID` from `fabric.list_datasets(workspace=WS_ID)` (match on name). The response includes the new report id.

## 8. Load the measures into the copy (only if needed)
The BIM copy already carries the source measures. Check in the copy's DAX query view:
`EVALUATE ROW ( "x", [<one measure name>] )`. If a measure is missing, paste the measure definitions into DAX query view and click **Update model with changes**.

**Clipboard tip (macOS):** paste DAX from files with `LC_ALL=en_US.UTF-8 pbcopy < file.dax`. Without UTF-8, characters such as `·` and `–` turn into garbage.

## 9. Adjust the public report
- Pages: right-click a page tab → Duplicate. Double-click a tab to rename it.
- Visuals: select a visual → Format → General → Properties → Size and Position fields. Clear the visual background (Effects → Background off) and set padding to 0 for HTML cards.
- Image visuals: Image source = *Select from data*, pick the measure, Image fit = *Fit*.
- Rebinding: select a visual → Visualizations → Values → remove the field (×) → search the Data pane → click the measure.
- Save, then Refresh visuals, then check the result in Viewing mode.
- Only change the public copy. Do not edit the original FinanceDashboard.

## 10. Publish to web (user approval required)
Only after the user says "publish FinanceDashboard":
1. In the public report: **File → Embed report → Publish to web (public)**.
2. Read the warning. Click **Continue**, then **Publish**.
3. Copy **Link you can send in email**.
4. Open the link in a private window to check it loads without signing in.

**Expect a delay:** after a change, Publish to web can take up to about an hour to show new pages or visuals. Re-check later before reporting a problem.

## 11. Keeping it current
- Set a scheduled refresh on the Import copy (Settings → Refresh → Scheduled refresh). Without it, the public numbers go stale.
- When the source model's measures change, update the copy's measures (step 8) and refresh.

## 12. Verification checklist
- [ ] Copy has the same tables, relationships and measures as the source (counts printed by the notebook).
- [ ] Refresh completes with no errors.
- [ ] Clone exists and its `datasetId` is the Import model's id.
- [ ] Each visual shows values (no blanks or errors).
- [ ] User has approved publishing.
- [ ] Public link opens without signing in; all pages present.

## Reference ids (Trading, for comparison)
| Item | Value |
|---|---|
| Trading-Dev workspace | `fe75eb04-2e1e-4499-ab7f-94ea15fa7c71` |
| Source model `sm_trading_gold` | Direct Lake |
| Import model `sm_trading_gold_import` | `9d86f729-3d0c-4a8a-8766-df0531fe5c25` |
| Source report `TradingDashboard` | `4185ef37-32ce-4b60-95e4-4b60a252cecd` |
| Public report `TradingDashboard - Public` | `bf84bf1c-7769-4cd7-bd7c-fcc85d972636` |

## Related files in this repo
- `fabric/notebooks/nb_build_import_model.py`: the copy notebook.
- `docs/how-to-publish-public-dashboard.md`: what was done for trading, step by step.
- `docs/publish-to-web.md`: short summary of the approach.
- `docs/report-build-guide.md`: visual slots and measures by page.
- `dax/`: measure library for the trading model.
