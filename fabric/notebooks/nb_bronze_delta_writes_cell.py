# === DELTA WRITES VIA ONELAKE (abfss) - fixes the FUSE rename failure ===
# write_deltalake() to /lakehouse/default/Tables/... fails with "Unable to rename
# file / Operation not permitted (os error 1)": the FUSE mount has no atomic
# rename, which Delta's commit protocol requires. The abfss:// endpoint does.
# Reading from the mount is fine, so bronze parquet is still read from Files/.
import glob, pandas as pd, notebookutils
from deltalake import write_deltalake
WS = "f256ccc7-77a6-4f99-aafe-c9ab2c2de2ac"
LH = "ca07c248-7b34-458b-9583-89d23c5945ab"
ONELAKE = f"abfss://{WS}@onelake.dfs.fabric.microsoft.com/{LH}"
SO = {"bearer_token": notebookutils.credentials.getToken("storage"), "use_fabric_endpoint": "true"}
BRONZE = "/lakehouse/default/Files/raw/alpaca"
latest = lambda d: sorted(glob.glob(f"{BRONZE}/{d}/ingest_date=*/alpaca_{d}.parquet"))[-1]
num = lambda df, cols: df.assign(**{c: pd.to_numeric(df[c], errors="coerce") for c in cols if c in df.columns})
ts = lambda df, cols: df.assign(**{c: pd.to_datetime(df[c], errors="coerce", utc=True) for c in cols if c in df.columns})
put = lambda name, df, mode="overwrite": [write_deltalake(f"{ONELAKE}/Tables/{name}", df.assign(ingested_at=pd.Timestamp.now(tz="UTC")), mode=mode, schema_mode="overwrite" if mode == "overwrite" else "merge", storage_options=SO), print(f"delta {name}: {len(df)} rows, {df.shape[1]} cols ({mode})")]
BARS = {"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume", "n": "trade_count", "vw": "vwap", "t": "bar_time_utc"}
mkbars = lambda df: ts(num(df, ["o", "h", "l", "c", "vw", "v", "n"]), ["t"]).rename(columns=BARS).assign(trade_date=lambda x: x["bar_time_utc"].dt.date.astype("string")).drop_duplicates(subset=["symbol", "trade_date"], keep="last")
put("alpaca_prices_equity", mkbars(pd.read_parquet(latest("prices_equity"))))
put("alpaca_prices_crypto", mkbars(pd.read_parquet(latest("prices_crypto"))))
put("alpaca_orders", ts(num(pd.read_parquet(latest("orders")), ["qty", "filled_qty", "filled_avg_price", "limit_price", "stop_price", "notional"]), ["created_at", "updated_at", "submitted_at", "filled_at", "expired_at", "canceled_at"]).drop_duplicates(subset=["id"], keep="last"))
put("alpaca_positions", num(pd.read_parquet(latest("positions")), ["qty", "avg_entry_price", "market_value", "cost_basis", "unrealized_pl", "unrealized_plpc", "current_price", "lastday_price", "change_today"]))
put("alpaca_account", num(pd.read_parquet(latest("account")), ["equity", "last_equity", "cash", "buying_power", "portfolio_value", "long_market_value", "short_market_value"]))
_live = ts(prices_live_df.copy(), ["trade_time_utc", "snapshot_at_utc"]) if "prices_live_df" in globals() and prices_live_df is not None else None
put("prices_live", _live, "append") if _live is not None and not _live.empty else print("prices_live: skipped (no snapshot DataFrame in this session)")
print("delta writes: done")
