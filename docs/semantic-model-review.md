# Semantic model review: sm_trading_gold

Reviewed 2 Nov 2026 against the gold tables (`TradingLakehouse`, Trading-Dev) and the model's diagram view. The model is open in **Viewing mode**, so nothing below has been applied yet.

## What the model has
- 8 tables: `gold_dim_date`, `gold_dim_strategy`, `gold_dim_symbol`, `gold_fact_account`, `gold_fact_orders`, `gold_fact_positions`, `gold_fact_prices_daily`, `gold_fact_trades`.
- Relationships visible in the diagram: `gold_dim_date` (1) → `gold_fact_orders`, `gold_fact_prices_daily`, `gold_fact_trades`, `gold_fact_positions`, `gold_fact_account` (many). All five are single-direction.
- No relationship lines reach `gold_dim_symbol` or `gold_dim_strategy`.
- No measures table is visible in the Data pane. The 116 measures in `dax/` are not loaded yet.

## Problems, by priority

### 1. Crypto P&L does not reconcile (high)
For the 233 crypto trades, `net` should equal `gross − fees`. It does not. Sum of `gross − fees` is **$1,228**, sum of `net` is **$630**, an unexplained gap of **−$597**. Every crypto row has non-zero `fees`, and the gap is about one commission per trade, so `fees` probably captures only one leg of the round trip.
Until this is resolved, the crypto figures ("Only crypto pays", crypto profit factor 1.14) and the headline net (−$4,711) carry about $600 of uncertainty. Check the silver notebook's commission logic before trusting these.

### 2. Symbol keys do not match between tables (high)
- `gold_dim_symbol` and `gold_fact_trades` use Binance-style pairs: `BTCUSDT`, `AVAXUSDT`.
- `gold_fact_prices_daily` uses Alpaca-style pairs: `BTCUSD`, `AVAXUSD`.
- So **5,426 price rows** have no matching symbol. Crypto prices cannot join to the dimension.
- Fix: add a `symbol_key` column to `gold_dim_symbol` (for example `BTC`, the existing `base` value) and to the price table, and relate on that. The `base` column already exists in `gold_dim_symbol`.

### 3. 31 filled orders have a blank symbol (medium)
`gold_fact_orders` has 31 rows where `symbol` is NULL or empty (all `filled`). They fall out of any symbol slicer. Find the source in the orders notebook and fix it in the silver layer.

### 4. Missing relationships (medium)
| From (one) | To (many) | Status |
|---|---|---|
| `gold_dim_strategy[strategy]` | `gold_fact_trades[strategy]` | missing (0 orphan rows, safe to add) |
| `gold_dim_symbol[symbol]` | `gold_fact_trades[symbol]` | missing (0 orphan rows, safe to add) |
| `gold_dim_symbol[symbol]` | `gold_fact_positions[symbol]` | missing (0 orphan rows) |
| `gold_dim_symbol[symbol]` | `gold_fact_orders[symbol]` | missing (31 blank rows will be orphans) |
| `gold_dim_symbol[symbol_key]` | `gold_fact_prices_daily[symbol_key]` | missing, needs fix 2 first |

### 5. Two date meanings in one column (medium)
`gold_fact_trades.Date` equals `closed_at` for all 355 trades, so it is the **close date**. Trade-open analysis (holding period, trades opened in a month) has no date. Add `opened_date` and relate it to `gold_dim_date` as an **inactive** relationship, then use `USERELATIONSHIP` in measures that need it. Rename `Date` to `closed_date` so the meaning is clear.

### 6. Inconsistent labels (medium)
Measures are safe because DAX text comparison ignores case, but visuals and slicers are not:
- `side`: `Long`, `LONG`, `Short`, `SHORT`
- `exit_type`: `Stop`/`stop`, `Manual`/`Manual_App`, `trailing`/`trailing_stop`/`Trailing`, `market`/`Market`, `limit`
Fix in the gold layer with a mapping table or `LOWER()`, so the slicers show one value per meaning.

### 7. Blank R and exit type (medium, expected for options)
- `r` is NULL for 155 trades: 31 options, 1 equity, and 123 crypto. Expectancy in R uses 200 of 355 trades, while expectancy in dollars uses all 355. Label the R measures "trades with planned risk".
- `exit_type` is NULL for 93 crypto trades. These fall into an "unknown" group in the exit charts.

### 8. Duplicate silver tables (low, housekeeping)
The lakehouse holds three versions of the silver layer: `trading.*`, `dbo.silver_trading_*` (underscore) and `dbo.silver_trading alpaca_*` (with spaces), plus `silver_alpaca_positions`. Keep one set and delete the others, so the model only sees the intended tables.

### 9. Model hygiene (low)
- Hide foreign-key columns on fact tables (`symbol`, `strategy`, `Date`, `trade_id`, `order_id`) so report authors use the dimension columns.
- Mark `gold_dim_date` as the date table.
- Sort `MonthName` by `Month`; `Weekday` by a numeric day column.
- Set `asset_class` and `side` as text with a fixed list, not free text.
- Add `Cumulative P&L` and drawdown measures to the model rather than in visuals.

## Fix order
1. Resolve the crypto net/fees gap (fix 1): this changes headline numbers.
2. Add `symbol_key` and the symbol and strategy relationships (fixes 2 and 4).
3. Add `opened_date` as an inactive relationship (fix 5).
4. Normalise labels and clean the blank symbols in silver (fixes 3 and 6).
5. Load `dax/_all-measures.dax` and set the hidden and sort settings (fix 9).

## What's needed to apply this
The model is in Viewing mode. To apply relationship and column changes, switch the model to **Editing mode** (or give me permission to open it), then the steps above can be run in the TMDL view.

## Applied 2 Nov 2026 (sm_trading_gold, Editing mode)
| Change | Result |
|---|---|
| Relationship `gold_fact_trades[strategy]` → `gold_dim_strategy[strategy]` (1:*, single, active) | added |
| Relationship `gold_fact_trades[symbol]` → `gold_dim_symbol[symbol]` (1:*, single, active) | added |
| Relationship `gold_fact_positions[symbol]` → `gold_dim_symbol[symbol]` | added **inactive**: an active one makes the path from `gold_dim_date` ambiguous (date → positions directly vs date → trades → symbol → positions) |
| `gold_dim_date` marked as date table (key `Date`) | already set, no change |
| 116 measures from `dax/_all-measures.dax` | saved to the model via DAX query view → Update model. Verified after a page reload: `[Win Rate]`, `[Net P&L]`, `[Title - The Desk]` and `[SVG - Equity Curve & Drawdown]` all resolve |

**Not applied (needs source changes first):**
- `symbol_key` column and the prices relationship: must be added in the gold notebook, not the model.
- `opened_date` role: needs a column in `gold_fact_trades`.
- Crypto `net` vs `gross − fees` gap: silver notebook fix.
- Hiding foreign-key columns and sorting `MonthName`/`Weekday`: cosmetic, not done.
- Measure formatting is set in the `.dax` files' header comments, not on the model, so format strings still need to be applied in the Properties pane. `Title - The Desk` contains a `"$0.0K"` format string that DAX doesn't use for display; fix when formatting.
