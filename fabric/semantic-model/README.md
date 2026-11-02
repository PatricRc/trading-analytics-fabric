# TradingSemanticModel

Direct Lake semantic model in the `Trading-Dev` workspace, built on `TradingLakehouse`.
That lakehouse reads the original `TradingLakeHouse` through a schema shortcut (`trading` → `dbo`).

## Tables (8)
gold_fact_trades, gold_fact_orders, gold_fact_positions, gold_fact_account,
gold_fact_prices_daily, plus the gold_dim_* dimensions.

## Still to do
- Relationships (facts → dim date / symbol / strategy)
- DAX measures (Net P&L, Win rate, Profit factor, Expectancy, Max drawdown)
- Cast the text price columns in `alpaca_prices_*` to decimal in silver
- Make labels consistent (Stop/stop, Long/LONG, Short/SHORT)
