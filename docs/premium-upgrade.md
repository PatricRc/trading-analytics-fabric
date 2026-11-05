# Premium upgrade: critique → fixes

The critique "Trading Dashboard vs. The World of Peaches" (4 Nov 2026) benchmarked this report against the 2026 Power BI Dataviz World Championship winner, [gusbavia/the-world-of-peaches](https://github.com/gusbavia/the-world-of-peaches). This log lists what changed in the public report (`TradingDashboard - Public`), what changed in the repo, and what is still open.

## Done

| # | Critique item | What changed | Where |
|---|---|---|---|
| 3.1 | Blank canvas on load; report opened on page 3 | A light **Cover** page is the first page and the landing page. It is one image visual, so something paints right away. | Report: page *Cover* |
| 3.2 | Profit factor "1.00" overlaps 0.84 | Reference moved into the subtitle: "break-even is 1.00 · only crypto clears it (1.14)" | `Card - Profit Factor HTML` |
| 3.2 | Equity-curve axis labels tiny and ambiguous ("$0", "00") | Y axis shows top, $0 and bottom in `$0.0K` at 12px, plus dashed gridlines and start/end dates | `SVG - Equity Curve & Drawdown` |
| 3.2 | Waterfall labels cramped at bar ends | Bars now run from x 150–760 and labels are right-aligned at 896, so they never touch | `SVG - P&L Waterfall` |
| 3.2 | "+$3,163 vs +$1,163" mismatch on Exit types | **Not a bug.** +$3,161 is the *Market* row and +$1,163 is *Take profit*. Both read `[Take Profit P&L]` in the same filter context. | — |
| 3.2 | Lollipop trade counts collide with value labels | Columns: Strategy · Trades · Net P&L · Win. The counts have their own column, and each row gets a win-rate chip. | `SVG - Strategy Lollipop` |
| 3.2 | Treemap labels truncated on small tiles | A label is drawn only if the ticker fits (`9px × len + 24`). Smaller tiles are listed as "+N smaller: CRWD −0.4%". | `SVG - Card Positions Treemap` |
| 3.2 | Stray link icons in card corners | Theme sets `visualHeader.show = false` for every visual | `powerbi/trading-theme.json` |
| 3.2 | Duplicate-value relationship / flat equity curve | Already fixed earlier: facts (*) → `gold_dim_date` (1); daily cumulative P&L on the date axis | Model |
| 3.3 | No design system | One token dict in `scripts/build_dax.py` generates the measures, `html/tokens.css` and the theme JSON | `scripts/build_dax.py`, `html/tokens.css` |
| 3.4 | Labels under 8pt; no display face | Georgia serif for page and card titles, sans for labels, uppercase eyebrows with tracking, `tabular-nums` on numbers, 10px labels raised to 12px | All HTML/SVG measures |
| 3.5 | Rail with no active state; redundant page bar | Rail has 5 items (Home · Book · Edge · Desk · Ledger) and a green active pill. An invisible vertical **Page navigator** (x0 y96, 72×380, 5×76px) makes it clickable. | `SVG - Rail*` + navigator visual on every page |
| 3.6 | Daily/Weekly toggle did nothing; pill "dropdowns" were decoration | The fake toggle and the "⌄" dropdown pills are gone. Header chips now state facts ("27 Aug – 30 Oct 2026", "As of 31 Oct 2026"). | `SVG - Header *`, `SVG - Card Equity Curve` |
| 3.7 | No cover or brand | Cover page: "The Book of a Paper Trader", 3 headline numbers, DataPat.ai mark, Explore → (page navigation), LinkedIn ↗ and Portfolio ↗ (web URL buttons) | `SVG - Cover` + 3 transparent buttons |
| 3.8 | Flat colour, no imagery | Cover hero drawn from the real data: one candle per trading day (open = previous cumulative P&L), radial gradient and grid texture. White cards get a hairline edge. | `SVG - Cover` |
| 3.9 | No in-chart markers | Equity curve: amber **PEAK** and ink **LOW** chips, kept inside the plot; "Now −$4,711" end label. Lollipop: win-rate chip per row. | SVG measures |
| 3.10 | No explore page | **The Ledger**: every strategy by asset class with trades, a net P&L heat bar, win %, avg R, PF and an EDGE / WATCH / CUT pill | `HTML - Ledger`, `Strategy Status` |
| 3.11 | No accessibility work | Gain/loss text colours pass WCAG AA on white (#23803A 5.0:1, #C9402F 4.9:1). ▲▼ arrows on signed KPIs. `Alt - *` measures written for the main visuals. | `11-alt-text/` |
| 3.12 | Repo packaging | Measures split by page with a comment header per file, plus tokens.css, a token-generated theme, README design process, screenshots and the live link | repo |

## Not done yet

| Item | Why | Next step |
|---|---|---|
| Field parameters (Asset / Grain, Cut) | Web modeling can't create field parameters in this tenant | Create them in Power BI Desktop, then republish |
| "How to read" bookmark overlay on each page | Bookmark flows are slow to build by browser automation | The cover's how-to-read strip covers the content for now. Add a bookmark overlay in Desktop. |
| Report-page tooltips (strategy mini equity curve) | Needs a tooltip page plus binding per visual | Build in Desktop |
| Binding `Alt - *` measures to Alt text → fx | Measures exist; binding is one click per visual | Format → General → Alt text → fx |
| Merging the 4 KPI HTML visuals into one per page | Would mean rebuilding page layouts | Do it with the PBIP export |
| PBIP / TMDL in the repo | Service-only edits so far | Download as PBIP and commit `src/` |

## How to re-apply after editing tokens
```bash
python3 scripts/build_dax.py .          # measures + html/tokens.css + powerbi/trading-theme.json
```
Paste `dax/_all-measures.dax` into the model's DAX query view, with measures on the `_measures` table, and click **Update model with changes**. Then import `powerbi/trading-theme.json` with Design → Import theme.

Publish to web caches the report. New pages can take up to about an hour to appear on the public link.
