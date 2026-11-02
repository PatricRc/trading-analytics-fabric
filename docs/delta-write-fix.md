# Delta write fix - status 2026-10-30

## What was done
Added a final cell to `nb_bronze_api_pulls` that writes Delta tables via the
OneLake `abfss://` endpoint with a bearer token, instead of the FUSE mount at
/lakehouse/default/Tables/. Source: fabric/cell_delta_writes.py

## Confirmed working
The cell ran in 2.4s and printed:
    delta alpaca_orders:    639 rows, 38 cols (overwrite)
    delta alpaca_positions:   6 rows, 18 cols (overwrite)
    delta alpaca_account:     1 rows, 36 cols (overwrite)
    prices_live: skipped (no snapshot DataFrame in this session)
    delta writes: done
=> The abfss:// approach commits successfully. The FUSE rename error is solved.

## Not yet confirmed
- The equity/crypto put() lines produced no visible output line.
- The SQL analytics endpoint still reports the OLD varchar schema for
  alpaca_orders even though the write above demonstrably succeeded.
  => endpoint metadata is lagging behind OneLake. Re-verify after it syncs.

## Outstanding cleanup (caused by a bad automation step)
The notebook now has 36 cells: the original 8 + my 1 + ~27 empty junk cells.
The junk came from text being typed while a cell was in command mode, which
fired single-key shortcuts (x = cut cell, b = insert below, etc). Autosave
persisted it. The original 8 cells and all their code are intact.
Cleanest fix: Fabric notebook History -> restore the pre-damage version, then
re-add the single cell from cell_delta_writes.py.

## Still to do
- prices_live: only populates on a full Run all (needs prices_live_df in scope).
- Rotate the Alpaca + Binance API keys (plaintext in cell 1).
