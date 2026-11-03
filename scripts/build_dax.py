"""Generate the DAX measure library for the Trading Analytics report.

Writes one .dax file per measure under dax/<folder>/ (same layout as the
city-sustainability-scorecard repo) plus dax/_all-measures.dax, a single
DEFINE script for the Power BI DAX query view ("Update model with changes").
"""
import os, re, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..")
HOME = "gold_fact_trades"   # measures live on this table, grouped by display folder
M = []                      # (folder, name, fmt, expr)

def m(folder, name, expr, fmt=""):
    M.append((folder, name, fmt, expr.strip("\n")))

# Palette (from the Paper design)
C = dict(LEAF="#4ED15A", LEAF6="#2E9E44", LEAF3="#A9E5AE", INK="#0F1712", MUT="#6A746C",
         HAIR="#E3E8E3", LOSS="#E0574C", LOSS3="#F2B5AE", MINT="#E3F5E5", DARK2="#1B2A20")
def col(s):
    for k, v in C.items():
        s = s.replace("{" + k + "}", v)
    return s

F_MONEY = '"$#,0;-$#,0;$0"'
F_PCT = '"0.0%"'

# ───────────────────────── 01 · base ─────────────────────────
B = "01-base"
m(B, "Trades", "COUNTROWS ( gold_fact_trades )", "#,0")
m(B, "Net P&L", "SUM ( gold_fact_trades[net] )", "$#,0;-$#,0;$0")
m(B, "Gross Wins", "CALCULATE ( [Net P&L], KEEPFILTERS ( gold_fact_trades[net] > 0 ) )", "$#,0;-$#,0;$0")
m(B, "Gross Losses", "CALCULATE ( [Net P&L], KEEPFILTERS ( gold_fact_trades[net] < 0 ) )", "$#,0;-$#,0;$0")
m(B, "Wins", "CALCULATE ( [Trades], KEEPFILTERS ( gold_fact_trades[is_win] = TRUE () ) )", "#,0")
m(B, "Losses", "[Trades] - [Wins]", "#,0")
m(B, "Win Rate", "DIVIDE ( [Wins], [Trades] )", "0.0%")
m(B, "Profit Factor", "DIVIDE ( [Gross Wins], ABS ( [Gross Losses] ) )", "0.00")
m(B, "Expectancy", "DIVIDE ( [Net P&L], [Trades] )", "$#,0.00;-$#,0.00")
m(B, "Avg R", "AVERAGE ( gold_fact_trades[r] )", '+0.00"R";-0.00"R"')
m(B, "Trades with R", "COUNT ( gold_fact_trades[r] )", "#,0")
m(B, "Cumulative P&L", """
VAR _d = MAX ( gold_dim_date[Date] )
RETURN
    CALCULATE (
        [Net P&L],
        FILTER ( ALLSELECTED ( gold_dim_date[Date] ), gold_dim_date[Date] <= _d )
    )""", "$#,0;-$#,0;$0")
m(B, "Peak Cumulative P&L", """
-- running high-water mark; the account starts at 0 so the peak never goes below 0
VAR _d = MAX ( gold_dim_date[Date] )
VAR _peak =
    MAXX (
        FILTER ( ALLSELECTED ( gold_dim_date[Date] ), gold_dim_date[Date] <= _d ),
        [Cumulative P&L]
    )
RETURN MAX ( _peak, 0 )""", "$#,0;-$#,0;$0")
m(B, "Drawdown", "[Cumulative P&L] - [Peak Cumulative P&L]", "$#,0;-$#,0;$0")
m(B, "Max Drawdown", """
MINX (
    FILTER ( ALLSELECTED ( gold_dim_date[Date] ), NOT ISBLANK ( [Net P&L] ) ),
    [Drawdown]
)""", "$#,0;-$#,0;$0")
m(B, "Peak P&L", """
MAXX ( FILTER ( ALLSELECTED ( gold_dim_date[Date] ), NOT ISBLANK ( [Net P&L] ) ), [Cumulative P&L] )""", "$#,0;-$#,0;$0")
m(B, "Low P&L", """
MINX ( FILTER ( ALLSELECTED ( gold_dim_date[Date] ), NOT ISBLANK ( [Net P&L] ) ), [Cumulative P&L] )""", "$#,0;-$#,0;$0")
m(B, "First Trade Date", "CALCULATE ( MIN ( gold_fact_trades[Date] ), ALLSELECTED ( gold_dim_date ) )", "d mmm yyyy")
m(B, "Last Trade Date", "CALCULATE ( MAX ( gold_fact_trades[Date] ), ALLSELECTED ( gold_dim_date ) )", "d mmm yyyy")

# ───────────────────────── 02 · page 1 · The Book ─────────────────────────
P1 = "02-page1-the-book"
m(P1, "Account Equity", """
VAR _d = MAX ( gold_fact_account[Date] )
RETURN CALCULATE ( SUM ( gold_fact_account[equity] ), gold_fact_account[Date] = _d, REMOVEFILTERS ( gold_dim_date ) )""", "$#,0")
m(P1, "Day P&L", """
VAR _d = MAX ( gold_fact_account[Date] )
RETURN CALCULATE ( SUM ( gold_fact_account[day_pnl] ), gold_fact_account[Date] = _d, REMOVEFILTERS ( gold_dim_date ) )""", "$#,0;-$#,0;$0")
m(P1, "Stop Exit P&L", 'CALCULATE ( [Net P&L], KEEPFILTERS ( gold_fact_trades[exit_type] = "stop" ) )  -- DAX text compare is case-insensitive: Stop + stop', "$#,0;-$#,0;$0")
m(P1, "Other Losses", "[Gross Losses] - [Stop Exit P&L]", "$#,0;-$#,0;$0")
m(P1, "Stop Share of Gains", "DIVIDE ( - [Stop Exit P&L], [Gross Wins] )", "0%")
m(P1, "Crypto P&L", 'CALCULATE ( [Net P&L], KEEPFILTERS ( gold_fact_trades[asset_class] = "crypto" ) )', "$#,0;-$#,0;$0")
m(P1, "Equity P&L", 'CALCULATE ( [Net P&L], KEEPFILTERS ( gold_fact_trades[asset_class] = "us_equity" ) )', "$#,0;-$#,0;$0")
m(P1, "Options P&L", 'CALCULATE ( [Net P&L], KEEPFILTERS ( gold_fact_trades[asset_class] = "us_option" ) )', "$#,0;-$#,0;$0")
m(P1, "Crypto Trades", 'CALCULATE ( [Trades], KEEPFILTERS ( gold_fact_trades[asset_class] = "crypto" ) )', "#,0")
m(P1, "Crypto Win Rate", 'CALCULATE ( [Win Rate], KEEPFILTERS ( gold_fact_trades[asset_class] = "crypto" ) )', "0%")
m(P1, "Crypto Profit Factor", 'CALCULATE ( [Profit Factor], KEEPFILTERS ( gold_fact_trades[asset_class] = "crypto" ) )', "0.00")
m(P1, "September P&L", "CALCULATE ( [Net P&L], KEEPFILTERS ( gold_dim_date[Month] = 9 ) )", "$#,0;-$#,0;$0")
m(P1, "October P&L", "CALCULATE ( [Net P&L], KEEPFILTERS ( gold_dim_date[Month] = 10 ) )", "$#,0;-$#,0;$0")
m(P1, "Title - The Book", """
-- conclusion title (style guide: the title states the finding)
VAR _net = [Net P&L]
RETURN
    "From " & FORMAT ( [Gross Wins] / 1000, "$0.0", "en-US" ) & "K" & " won to "
        & FORMAT ( ABS ( _net ) / 1000, "$0.0", "en-US" ) & "K" & IF ( _net < 0, " lost", " kept" )""")
m(P1, "Subtitle - The Book", """
"Is the account growing? · " & FORMAT ( [Trades], "#,0" ) & " closed trades · "
    & FORMAT ( [First Trade Date], "d mmm", "en-US" ) & " – " & FORMAT ( [Last Trade Date], "d mmm yyyy", "en-US" )""")

# ───────────────────────── 03 · page 2 · The Edge ─────────────────────────
P2 = "03-page2-the-edge"
m(P2, "Lost Past -1R P&L", "CALCULATE ( [Net P&L], KEEPFILTERS ( gold_fact_trades[r] < -1 ) )", "$#,0;-$#,0;$0")
m(P2, "Lost Past -1R Trades", "CALCULATE ( [Trades], KEEPFILTERS ( gold_fact_trades[r] < -1 ) )", "#,0")
m(P2, "Won 1R+ P&L", "CALCULATE ( [Net P&L], KEEPFILTERS ( gold_fact_trades[r] >= 1 ) )", "$#,0;-$#,0;$0")
m(P2, "Won 1R+ Trades", "CALCULATE ( [Trades], KEEPFILTERS ( gold_fact_trades[r] >= 1 ) )", "#,0")
m(P2, "Stop Exits", 'CALCULATE ( [Trades], KEEPFILTERS ( gold_fact_trades[exit_type] = "stop" ) )', "#,0")
m(P2, "Stop Exit Recovery %", 'COALESCE ( CALCULATE ( [Win Rate], KEEPFILTERS ( gold_fact_trades[exit_type] = "stop" ) ), 0 )  -- no winning stop exits -> 0%, not blank', "0%")
m(P2, "Trailing P&L", 'CALCULATE ( [Net P&L], KEEPFILTERS ( gold_fact_trades[exit_type] IN { "trailing", "trailing_stop" } ) )', "$#,0;-$#,0;$0")
m(P2, "Trailing Win Rate", 'CALCULATE ( [Win Rate], KEEPFILTERS ( gold_fact_trades[exit_type] IN { "trailing", "trailing_stop" } ) )', "0%")
m(P2, "Market Exit P&L", 'CALCULATE ( [Net P&L], KEEPFILTERS ( gold_fact_trades[exit_type] = "market" ) )', "$#,0;-$#,0;$0")
m(P2, "Manual Exit P&L", 'CALCULATE ( [Net P&L], KEEPFILTERS ( gold_fact_trades[exit_type] IN { "manual", "manual_app" } ) )', "$#,0;-$#,0;$0")
m(P2, "Take Profit P&L", 'CALCULATE ( [Net P&L], KEEPFILTERS ( gold_fact_trades[exit_type] = "take_profit" ) )', "$#,0;-$#,0;$0")
m(P2, "Take Profit Trades", 'CALCULATE ( [Trades], KEEPFILTERS ( gold_fact_trades[exit_type] = "take_profit" ) )', "#,0")
m(P2, "Take Profit Avg R", 'CALCULATE ( [Avg R], KEEPFILTERS ( gold_fact_trades[exit_type] = "take_profit" ) )', '0.00"R"')
m(P2, "Short P&L", 'CALCULATE ( [Net P&L], KEEPFILTERS ( gold_fact_trades[side] = "short" ) )', "$#,0;-$#,0;$0")
m(P2, "Long P&L", 'CALCULATE ( [Net P&L], KEEPFILTERS ( gold_fact_trades[side] = "long" ) )', "$#,0;-$#,0;$0")
m(P2, "Short Trades", 'CALCULATE ( [Trades], KEEPFILTERS ( gold_fact_trades[side] = "short" ) )', "#,0")
m(P2, "Long Trades", 'CALCULATE ( [Trades], KEEPFILTERS ( gold_fact_trades[side] = "long" ) )', "#,0")
m(P2, "Short Win Rate", 'CALCULATE ( [Win Rate], KEEPFILTERS ( gold_fact_trades[side] = "short" ) )', "0%")
m(P2, "Long Win Rate", 'CALCULATE ( [Win Rate], KEEPFILTERS ( gold_fact_trades[side] = "long" ) )', "0%")
m(P2, "Long Share of Trades", "DIVIDE ( [Long Trades], [Trades] )", "0%")
m(P2, "Strategy Rank Best", """
-- 1 = best strategy by net P&L within the current selection
IF (
    ISINSCOPE ( gold_fact_trades[strategy] ),
    RANKX ( ALLSELECTED ( gold_fact_trades[strategy] ), [Net P&L], , DESC, DENSE )
)""", "0")
m(P2, "Strategy Rank Worst", """
IF (
    ISINSCOPE ( gold_fact_trades[strategy] ),
    RANKX ( ALLSELECTED ( gold_fact_trades[strategy] ), [Net P&L], , ASC, DENSE )
)""", "0")
m(P2, "Strategy Top-Bottom 4 Filter", """
-- visual-level filter: is 1 for the 4 best and 4 worst strategies
IF ( [Strategy Rank Best] <= 4 || [Strategy Rank Worst] <= 4, 1, 0 )""", "0")
m(P2, "Strategies", "DISTINCTCOUNT ( gold_fact_trades[strategy] )", "#,0")
m(P2, "Title - The Edge", """
"Expectancy " & FORMAT ( [Expectancy], "$#,0.00;-$#,0.00", "en-US" ) & " per trade · "
    & IF ( [Short P&L] > [Long P&L], "shorts carry the book", "longs carry the book" )""")

# ───────────────────────── 04 · page 3 · The Desk ─────────────────────────
P3 = "04-page3-the-desk"
def acct(name, c, fmt="$#,0"):
    m(P3, name, f"""
VAR _d = MAX ( gold_fact_account[Date] )
RETURN CALCULATE ( SUM ( gold_fact_account[{c}] ), gold_fact_account[Date] = _d, REMOVEFILTERS ( gold_dim_date ) )""", fmt)
acct("Cash", "cash"); acct("Buying Power", "buying_power"); acct("Long Market Value", "long_market_value")
m(P3, "Buying Power x Equity", "DIVIDE ( [Buying Power], [Account Equity] )", '0.0"x"')
m(P3, "Position Market Value", "SUM ( gold_fact_positions[market_value] )", "$#,0")
m(P3, "Capital Deployed %", "DIVIDE ( [Position Market Value], [Account Equity] )", "0%")
m(P3, "Cash %", "DIVIDE ( [Cash], [Account Equity] )", "0%")
m(P3, "Unrealized P&L", "SUM ( gold_fact_positions[unrealized_pl] )", "$#,0;-$#,0;$0")
m(P3, "Unrealized %", "DIVIDE ( [Unrealized P&L], SUM ( gold_fact_positions[cost_basis] ) )", "+0.0%;-0.0%")
m(P3, "Open Positions", "COUNTROWS ( gold_fact_positions )", "#,0")
m(P3, "Positions Up", "CALCULATE ( [Open Positions], KEEPFILTERS ( gold_fact_positions[unrealized_pl] > 0 ) )", "#,0")
m(P3, "Positions Down", "CALCULATE ( [Open Positions], KEEPFILTERS ( gold_fact_positions[unrealized_pl] < 0 ) )", "#,0")
m(P3, "Position Return %", "DIVIDE ( [Unrealized P&L], SUM ( gold_fact_positions[cost_basis] ) )", "+0.00%;-0.00%")
m(P3, "Top Position Symbol", """
MAXX ( TOPN ( 1, VALUES ( gold_fact_positions[symbol] ), [Position Market Value], DESC ), gold_fact_positions[symbol] )""")
m(P3, "Top Position Share", """
DIVIDE (
    MAXX ( VALUES ( gold_fact_positions[symbol] ), [Position Market Value] ),
    [Position Market Value]
)""", "0%")
m(P3, "Top Position Unrealized", """
VAR _s = [Top Position Symbol]
RETURN CALCULATE ( [Unrealized P&L], gold_fact_positions[symbol] = _s )""", "$#,0;-$#,0;$0")
m(P3, "Orders", "COUNTROWS ( gold_fact_orders )", "#,0")
m(P3, "Filled Orders", 'CALCULATE ( [Orders], KEEPFILTERS ( gold_fact_orders[status] = "filled" ) )', "#,0")
m(P3, "Canceled Orders", 'CALCULATE ( [Orders], KEEPFILTERS ( gold_fact_orders[status] = "canceled" ) )', "#,0")
m(P3, "Expired Orders", 'CALCULATE ( [Orders], KEEPFILTERS ( gold_fact_orders[status] = "expired" ) )', "#,0")
m(P3, "Working Orders", "[Orders] - [Filled Orders] - [Canceled Orders] - [Expired Orders]", "#,0")
m(P3, "Canceled Sells", 'CALCULATE ( [Canceled Orders], KEEPFILTERS ( gold_fact_orders[side] = "sell" ) )', "#,0")
m(P3, "Fill Rate", "DIVIDE ( [Filled Orders], [Orders] )", "0.0%")
m(P3, "Cancel Rate", "DIVIDE ( [Canceled Orders], [Orders] )", "0%")
m(P3, "Turnover", 'CALCULATE ( SUM ( gold_fact_orders[notional] ), KEEPFILTERS ( gold_fact_orders[status] = "filled" ) )', "$#,0")
m(P3, "Turnover x Equity", "DIVIDE ( [Turnover], [Account Equity] )", '0"x"')
m(P3, "Equities Priced", 'CALCULATE ( DISTINCTCOUNT ( gold_fact_prices_daily[symbol] ), KEEPFILTERS ( gold_fact_prices_daily[asset_class] = "equity" ) )', "#,0")
m(P3, "Crypto Priced", 'CALCULATE ( DISTINCTCOUNT ( gold_fact_prices_daily[symbol] ), KEEPFILTERS ( gold_fact_prices_daily[asset_class] = "crypto" ) )', "#,0")
m(P3, "Equities Tracked", "[Equities Priced]  -- every tracked equity currently has daily bars", "#,0")
m(P3, "Crypto Pairs Tracked", "30  -- universe size from the bot config; 14 pairs are not listed on Alpaca", "#,0")
m(P3, "Title - The Desk", """
FORMAT ( [Cash] / 1000, "$0.0", "en-US" ) & "K" & " sitting in cash · "
    & FORMAT ( [Capital Deployed %], "0%" ) & " of equity deployed" """)

# ───────────────────────── 05 · HTML cards (HTML Content visual) ─────────────────────────
H = "05-html-cards"
CARD_CSS = col("font-family:Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif;border-radius:18px;padding:18px 22px;height:156px;box-sizing:border-box;position:relative;overflow:hidden")
PANEL_CSS = CARD_CSS.replace("height:156px", "height:322px")

def bars(heights_expr):
    """mini bar strip: heights_expr is a DAX list of (value, color) pairs built inline"""
    return heights_expr

def card(name, label, value_expr, sub_expr, dark=False, accent_expr=None, mini=None):
    bg = col("{INK}") if dark else "#FFFFFF"
    fg = "#FFFFFF" if dark else col("{INK}")
    mut = "rgba(255,255,255,.62)" if dark else col("{MUT}")
    vcol = accent_expr or f'"{fg}"'
    mini_part = f' & {mini}' if mini else ''
    m(H, name, f"""
VAR _val = {value_expr}
VAR _sub = {sub_expr}
VAR _color = {vcol}
RETURN
    "<div style='{CARD_CSS};background:{bg};color:{fg}'>"
        & "<div style='font-size:14px;font-weight:600;color:{mut}'>{label}</div>"
        & "<div style='font-size:44px;font-weight:800;letter-spacing:-.02em;margin-top:14px;color:" & _color & "'>" & _val & "</div>"
        & "<div style='font-size:13px;color:{mut};margin-top:8px'>" & _sub & "</div>"{mini_part}
        & "</div>" """)

SIGN = lambda e: f'IF ( {e} < 0, "{C["LOSS"]}", "{C["LEAF6"]}" )'
MINI = lambda a, b, c: (  # three proportional bars in the corner: values a,b,c (DAX), colours fixed
    f'"<div style=\'position:absolute;right:22px;bottom:22px;display:flex;gap:5px;align-items:flex-end;height:48px\'>"'
    f' & "<i style=\'width:9px;background:{C["LOSS"]};height:" & FORMAT ( 48 * DIVIDE ( ABS ( {a} ), MAX ( ABS ( {a} ), MAX ( ABS ( {b} ), ABS ( {c} ) ) ) ), "0", "en-US" ) & "px\'></i>"'
    f' & "<i style=\'width:9px;background:{C["LEAF6"]};height:" & FORMAT ( 48 * DIVIDE ( ABS ( {b} ), MAX ( ABS ( {a} ), MAX ( ABS ( {b} ), ABS ( {c} ) ) ) ), "0", "en-US" ) & "px\'></i>"'
    f' & "<i style=\'width:9px;background:{C["LEAF"]};height:" & FORMAT ( 48 * DIVIDE ( ABS ( {c} ), MAX ( ABS ( {a} ), MAX ( ABS ( {b} ), ABS ( {c} ) ) ) ), "0", "en-US" ) & "px\'></i>"'
    f' & "</div>"')

# Page 1
card("Card - Account Equity HTML", "Account equity", 'FORMAT ( [Account Equity], "$#,0", "en-US" )',
     '"<span style=\'background:" & IF ( [Day P&L] < 0, "' + C["LOSS"] + '", "' + C["LEAF6"] + '" ) & ";color:#fff;border-radius:8px;padding:2px 7px;font-weight:700\'>" & FORMAT ( [Day P&L], "+$#,0;-$#,0", "en-US" ) & "</span> today"',
     dark=True, mini=MINI("[Day P&L]", "[Account Equity]/100", "[Account Equity]/200"))
card("Card - Net Closed P&L HTML", "Net closed P&L", 'FORMAT ( [Net P&L], "+$#,0;-$#,0", "en-US" )',
     '"crypto · equity · options"', accent_expr=SIGN("[Net P&L]"), mini=MINI("[Options P&L]", "[Equity P&L]", "[Crypto P&L]"))
card("Card - Win Rate HTML", "Win rate", 'FORMAT ( [Win Rate], "0.0%", "en-US" )',
     'FORMAT ( [Wins], "#,0" ) & " won · " & FORMAT ( [Losses], "#,0" ) & " lost"', mini=MINI("[Losses]", "[Wins]", "[Wins]"))
card("Card - Profit Factor HTML", "Profit factor", 'FORMAT ( [Profit Factor], "0.00", "en-US" ) & "<span style=\'font-size:15px;color:' + C["MUT"] + '\'>/1.00</span>"',
     '"only crypto clears 1.0 (" & FORMAT ( [Crypto Profit Factor], "0.00", "en-US" ) & ")"', mini=MINI("[Gross Losses]", "[Gross Wins]", "[Gross Wins]*[Crypto Profit Factor]/2"))
# Page 2
card("Card - Expectancy HTML", "Expectancy per trade", 'FORMAT ( [Expectancy], "+$#,0.00;-$#,0.00", "en-US" )',
     'FORMAT ( [Avg R], "+0.00;-0.00", "en-US" ) & "R" & " avg R-multiple"', dark=True, mini=MINI("[Gross Losses]", "[Gross Wins]", "[Net P&L]"))
card("Card - Lost Past -1R HTML", "Lost past −1R", 'FORMAT ( [Lost Past -1R P&L] / 1000, "+$0.0;-$0.0", "en-US" ) & "K"',
     'FORMAT ( [Lost Past -1R Trades], "#,0" ) & " trades slipped their stop"', accent_expr=f'"{C["LOSS"]}"')
card("Card - Won 1R+ HTML", "Won 1R or more", 'FORMAT ( [Won 1R+ P&L] / 1000, "+$0.0;-$0.0", "en-US" ) & "K"',
     'FORMAT ( [Won 1R+ Trades], "#,0" ) & " trades · the real edge"', accent_expr=f'"{C["LEAF6"]}"')
card("Card - Stop Exits HTML", "Stop exits", 'FORMAT ( [Stop Exits], "#,0" ) & " trades"',
     'FORMAT ( [Stop Exit Recovery %], "0%" ) & " recovered · " & FORMAT ( [Stop Exit P&L], "$#,0;-$#,0", "en-US" )')
# Page 3
card("Card - Capital Deployed HTML", "Capital deployed", 'FORMAT ( [Capital Deployed %], "0%" )',
     '"<b style=\'color:' + C["LEAF"] + '\'>" & FORMAT ( [Position Market Value] / 1000, "$0.0", "en-US" ) & "K" & "</b> of " & FORMAT ( [Account Equity] / 1000, "$0.0", "en-US" ) & "K" & " equity"', dark=True)
card("Card - Unrealized P&L HTML", "Unrealized P&L", 'FORMAT ( [Unrealized P&L], "+$#,0;-$#,0", "en-US" )',
     'FORMAT ( [Unrealized %], "+0.0%;-0.0%", "en-US" ) & " on cost · " & [Positions Up] & " up, " & [Positions Down] & " down"', accent_expr=SIGN("[Unrealized P&L]"))
card("Card - Fill Rate HTML", "Fill rate", 'FORMAT ( [Fill Rate], "0.0%", "en-US" )',
     'FORMAT ( [Filled Orders], "#,0" ) & " of " & FORMAT ( [Orders], "#,0" ) & " orders filled"', mini=MINI("[Canceled Orders]", "[Filled Orders]", "[Working Orders]"))
card("Card - Turnover HTML", "Turnover", 'FORMAT ( [Turnover] / 1000000, "$0.0", "en-US" ) & "M"',
     'FORMAT ( [Turnover x Equity], "0", "en-US" ) & "× equity"')

# Insight panels
def panel(name, body, dark=False):
    bg = col("{INK}") if dark else col("{MINT}")
    fg = "#FFFFFF" if dark else col("{INK}")
    m(H, name, f'"<div style=\'{PANEL_CSS};background:{bg};color:{fg};padding:26px 28px\'>" & {body} & "</div>"')

ROW = lambda title, sub, good: (f'"<div style=\'display:flex;gap:12px;align-items:center;margin-top:14px\'>'
    f'<span style=\'width:30px;height:30px;border-radius:15px;background:rgba(46,158,68,.15);display:grid;place-items:center;color:{C["LEAF6"] if good else C["LOSS"]}\'>&#9679;</span>'
    f'<span><b style=\'font-size:17px\'>" & {title} & "</b><br><span style=\'font-size:11px;color:{C["MUT"]}\'>" & {sub} & "</span></span></div>"')
BIG = lambda v, sub, color=C["INK"]: (f'"<div style=\'font-size:56px;font-weight:800;letter-spacing:-.03em;color:{color}\'>" & {v} & "</div>"'
    f' & "<div style=\'font-size:13px;font-weight:600;margin-top:2px\'>" & {sub} & "</div>"')

panel("Panel - Max Drawdown HTML",
      BIG('FORMAT ( [Max Drawdown], "$#,0;-$#,0", "en-US" )', '"max drawdown from the " & FORMAT ( [First Trade Date], "d mmm", "en-US" ) & " peak"')
      + " & " + ROW('"September " & FORMAT ( [September P&L], "$#,0;-$#,0", "en-US" )', '"the bleed"', False)
      + " & " + ROW('"October " & FORMAT ( [October P&L], "$#,0;-$#,0", "en-US" )', '"bleeding stopped"', True))
EXIT_BAR = lambda label, m_: (
    f'"<div style=\'display:flex;align-items:center;gap:10px;margin-top:7px;font-size:12px\'>'
    f'<span style=\'width:84px;font-weight:600\'>{label}</span>'
    f'<span style=\'flex:1;height:9px;border-radius:5px;background:rgba(15,23,18,.08);position:relative\'>'
    f'<span style=\'position:absolute;left:0;top:0;bottom:0;border-radius:5px;background:{C["LEAF6"]};width:" & FORMAT ( DIVIDE ( MAX ( [{m_}], 0 ), _max ) * 100, "0", "en-US" ) & "%\'></span></span>'
    f'<span style=\'width:70px;text-align:right;font-weight:700;color:{C["LEAF6"]}\'>" & FORMAT ( [{m_}], "+$#,0;-$#,0", "en-US" ) & "</span></div>"')
m(H, "Panel - Trailing Stops HTML", f"""
VAR _max = MAX ( MAX ( [Market Exit P&L], [Trailing P&L] ), MAX ( [Manual Exit P&L], [Take Profit P&L] ) )
VAR _best = TOPN ( 1, FILTER ( ADDCOLUMNS ( VALUES ( gold_fact_trades[strategy] ), "@n", [Trades], "@w", [Win Rate], "@r", [Avg R] ), [@n] >= 10 ), [@w], DESC, [@n], DESC )
RETURN
    "<div style='{PANEL_CSS};background:{C["MINT"]};color:{C["INK"]};padding:24px 28px'>"
        & "<div style='font-size:48px;font-weight:800;letter-spacing:-.03em;color:{C["LEAF6"]}'>" & FORMAT ( [Trailing P&L], "+$#,0;-$#,0", "en-US" ) & "</div>"
        & "<div style='font-size:13px;font-weight:600;margin:2px 0 6px'>from trailing stops · " & FORMAT ( [Trailing Win Rate], "0%" ) & " win</div>"
        & {EXIT_BAR("Market", "Market Exit P&L")} & {EXIT_BAR("Trailing", "Trailing P&L")}
        & {EXIT_BAR("Manual", "Manual Exit P&L")} & {EXIT_BAR("Take profit", "Take Profit P&L")}
        & {ROW('"Take profit " & FORMAT ( [Take Profit P&L], "+$#,0", "en-US" )', 'FORMAT ( [Take Profit Trades], "0" ) & " exits · 100% win · avg " & FORMAT ( [Take Profit Avg R], "0.00", "en-US" ) & "R"', True)}
        & {ROW('MAXX ( _best, gold_fact_trades[strategy] ) & " · " & FORMAT ( MAXX ( _best, [@w] ), "0%" ) & " win"', 'FORMAT ( MAXX ( _best, [@n] ), "0" ) & " trades · " & FORMAT ( MAXX ( _best, [@r] ), "+0.00;-0.00", "en-US" ) & "R avg · most reliable"', True)}
        & "</div>" """)
m(H, "Panel - Cash HTML", f"""
VAR _eq = [Account Equity]
VAR _pos = ADDCOLUMNS ( VALUES ( gold_fact_positions[symbol] ), "@mv", [Position Market Value], "@r", [Position Return %] )
VAR _strip = CONCATENATEX ( _pos,
    "<span title='" & gold_fact_positions[symbol] & "' style='display:inline-block;height:12px;width:" & FORMAT ( DIVIDE ( [@mv], _eq ) * 100, "0.00", "en-US" ) & "%;background:"
        & IF ( [@r] >= 0.01, "{C["LEAF6"]}", IF ( [@r] >= 0, "{C["LEAF3"]}", IF ( [@r] > -0.01, "{C["LOSS3"]}", "{C["LOSS"]}" ) ) ) & "'></span>",
    "", [@mv], DESC )
VAR _names = CONCATENATEX ( _pos, gold_fact_positions[symbol], " · ", [@mv], DESC )
RETURN
    "<div style='{PANEL_CSS};background:{C["MINT"]};color:{C["INK"]};padding:24px 28px'>"
        & "<div style='display:flex;justify-content:space-between;align-items:flex-start'><div>"
        & "<div style='font-size:52px;font-weight:800;letter-spacing:-.03em'>" & FORMAT ( [Cash] / 1000, "$0.0", "en-US" ) & "K</div>"
        & "<div style='font-size:13px;font-weight:600;margin-top:2px'><span style='color:{C["LEAF6"]}'>&#9675;</span> sitting in cash · " & FORMAT ( [Cash %], "0%" ) & " of equity</div></div>"
        & "<img style='width:92px;height:92px' src=\"\"\" & [SVG - Cash Donut] & \"\"\"/></div>"
        & "<div style='margin-top:18px;height:12px;border-radius:6px;overflow:hidden;background:{C["HAIR"]};white-space:nowrap;font-size:0'>" & _strip & "</div>"
        & "<div style='display:flex;justify-content:space-between;font-size:10px;color:{C["MUT"]};margin-top:5px'><span>" & _names & "</span><span>Cash " & FORMAT ( [Cash %], "0%" ) & "</span></div>"
        & {ROW('"Buying power " & FORMAT ( [Buying Power], "$#,0", "en-US" )', 'FORMAT ( [Buying Power x Equity], "0.0", "en-US" ) & "× equity · margin unused"', True)}
        & {ROW('[Top Position Symbol] & " is " & FORMAT ( [Top Position Share], "0%" ) & " of exposure"', 'FORMAT ( [Top Position Unrealized], "+$#,0;-$#,0", "en-US" ) & " unrealized"', True)}
        & "</div>" """)
panel("Panel - Shorts vs Longs HTML",
      '"<div style=\'font-size:15px;font-weight:700;margin-bottom:12px\'>" & IF ( [Short P&L] > [Long P&L], "Shorts carry the book", "Longs carry the book" ) & "</div>"'
      ' & "<div style=\'display:flex;gap:10px\'>"'
      f' & "<div style=\'flex:1;background:{C["DARK2"]};border-radius:12px;padding:12px\'><div style=\'font-size:11px;opacity:.6\'>Short · " & [Short Trades] & "</div><div style=\'font-size:26px;font-weight:800;color:{C["LEAF"]}\'>" & FORMAT ( [Short P&L], "+$#,0;-$#,0", "en-US" ) & "</div><div style=\'font-size:11px;opacity:.6\'>" & FORMAT ( [Short Win Rate], "0%" ) & " win</div></div>"'
      f' & "<div style=\'flex:1;background:{C["DARK2"]};border-radius:12px;padding:12px\'><div style=\'font-size:11px;opacity:.6\'>Long · " & [Long Trades] & "</div><div style=\'font-size:26px;font-weight:800;color:{C["LOSS"]}\'>" & FORMAT ( [Long P&L], "+$#,0;-$#,0", "en-US" ) & "</div><div style=\'font-size:11px;opacity:.6\'>" & FORMAT ( [Long Win Rate], "0%" ) & " win</div></div>"'
      ' & "</div>"', dark=True)

# ───────────────────────── 06 · SVG visuals (Image URL / HTML Content) ─────────────────────────
S = "06-svg-visuals"
SVG_END = 'RETURN "data:image/svg+xml;utf8," & SUBSTITUTE ( SUBSTITUTE ( _svg, "%", "%25" ), "#", "%23" )  -- URI-encode % first, then #'
TRADE_DATES = 'FILTER ( ALLSELECTED ( gold_dim_date[Date] ), NOT ISBLANK ( [Net P&L] ) )'

m(S, "SVG - Equity Curve & Drawdown", col(f"""
-- line = cumulative closed P&L; red band underneath = drawdown from the running peak
VAR _W = 900  VAR _H = 220  VAR _L = 44  VAR _R = 8
VAR _t = ADDCOLUMNS ( {TRADE_DATES}, "@cum", [Cumulative P&L], "@dd", [Drawdown] )
VAR _d0 = MINX ( _t, gold_dim_date[Date] )  VAR _d1 = MAXX ( _t, gold_dim_date[Date] )
VAR _hi = MAX ( 0, MAXX ( _t, [@cum] ) )  VAR _lo = MIN ( 0, MINX ( _t, [@cum] ) )
VAR _ddlo = MIN ( -1, MINX ( _t, [@dd] ) )
VAR _span = MAX ( 1, INT ( _d1 - _d0 ) )
VAR _pts = ADDCOLUMNS ( _t,
    "@x", _L + INT ( gold_dim_date[Date] - _d0 ) / _span * ( _W - _L - _R ),
    "@y", 10 + ( _hi - [@cum] ) / MAX ( 1, _hi - _lo ) * 120,
    "@uy", 150 + [@dd] / _ddlo * 50 )
VAR _line = CONCATENATEX ( _pts, FORMAT ( [@x], "0.0", "en-US" ) & "," & FORMAT ( [@y], "0.0", "en-US" ), " ", gold_dim_date[Date], ASC )
VAR _under = CONCATENATEX ( _pts, FORMAT ( [@x], "0.0", "en-US" ) & "," & FORMAT ( [@uy], "0.0", "en-US" ), " ", gold_dim_date[Date], ASC )
VAR _y0 = 10 + _hi / MAX ( 1, _hi - _lo ) * 120
VAR _last = TOPN ( 1, _pts, gold_dim_date[Date], DESC )
VAR _lx = MAXX ( _last, [@x] )  VAR _ly = MAXX ( _last, [@y] )
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 900 220' font-family='Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif' >"
        & "<line x1='44' x2='892' y1='" & FORMAT ( _y0, "0.0", "en-US" ) & "' y2='" & FORMAT ( _y0, "0.0", "en-US" ) & "' stroke='{{HAIR}}'/>"
        & "<text x='0' y='" & FORMAT ( _y0 + 4, "0.0", "en-US" ) & "' font-size='10' fill='{{MUT}}'>$0</text>"
        & "<polyline points='" & _line & "' fill='none' stroke='{{LEAF6}}' stroke-width='2' stroke-linejoin='round'/>"
        & "<line x1='44' x2='892' y1='150' y2='150' stroke='{{HAIR}}'/>"
        & "<text x='0' y='162' font-size='10' fill='{{MUT}}'>DD</text>"
        & "<polygon points='44,150 " & _under & " " & FORMAT ( _lx, "0.0", "en-US" ) & ",150' fill='{{LOSS}}' fill-opacity='.22' stroke='{{LOSS}}' stroke-width='1.2'/>"
        & "<circle cx='" & FORMAT ( _lx, "0.0", "en-US" ) & "' cy='" & FORMAT ( _ly, "0.0", "en-US" ) & "' r='5' fill='{{LEAF6}}'/>"
        & "<text x='" & FORMAT ( _lx - 8, "0.0", "en-US" ) & "' y='" & FORMAT ( _ly - 10, "0.0", "en-US" ) & "' font-size='12' font-weight='700' text-anchor='end' fill='{{INK}}'>" & FORMAT ( [Net P&L], "$#,0;-$#,0", "en-US" ) & "</text>"
        & "<text x='300' y='214' font-size='10' font-weight='600' fill='{{LOSS}}'>Max drawdown " & FORMAT ( _ddlo, "$#,0;-$#,0", "en-US" ) & "</text>"
        & "</svg>"
{SVG_END}"""))

m(S, "SVG - P&L Waterfall", col(f"""
-- gross wins → stop exits → other losses → net (bars start from zero, per the style guide)
VAR _gw = [Gross Wins]  VAR _st = [Stop Exit P&L]  VAR _ot = [Other Losses]  VAR _net = [Net P&L]
VAR _min = MIN ( 0, _net )  VAR _max = _gw
VAR _X = ( v ) => 0   -- placeholder, Power BI does not support lambdas; see inline math below
VAR _sc = 560 / ( _max - _min )
VAR _z = 300 - _min * _sc
VAR _x1 = _z + _gw * _sc  VAR _x2 = _x1 + _st * _sc  VAR _x3 = _x2 + _ot * _sc
VAR _row = ( 0 )
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 900 150' font-family='Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif' font-size='13'>"
        & "<line x1='" & FORMAT ( _z, "0.0", "en-US" ) & "' x2='" & FORMAT ( _z, "0.0", "en-US" ) & "' y1='0' y2='136' stroke='#BFC8C0'/>"
        & "<text x='0' y='19' fill='{{INK}}'>Gross wins</text><rect x='" & FORMAT ( _z, "0.0", "en-US" ) & "' y='4' width='" & FORMAT ( ( _x1 - _z ), "0.0", "en-US" ) & "' height='22' rx='6' fill='{{LEAF6}}'/>"
        & "<text x='900' y='19' text-anchor='end' font-weight='700' fill='{{LEAF6}}'>" & FORMAT ( _gw, "+$#,0", "en-US" ) & "</text>"
        & "<text x='0' y='53' fill='{{INK}}'>Stop exits</text><rect x='" & FORMAT ( _x2, "0.0", "en-US" ) & "' y='38' width='" & FORMAT ( ( _x1 - _x2 ), "0.0", "en-US" ) & "' height='22' rx='6' fill='{{LOSS}}'/>"
        & "<text x='900' y='53' text-anchor='end' font-weight='700' fill='{{LOSS}}'>" & FORMAT ( _st, "$#,0;-$#,0", "en-US" ) & "</text>"
        & "<text x='0' y='87' fill='{{INK}}'>Other losses</text><rect x='" & FORMAT ( _x3, "0.0", "en-US" ) & "' y='72' width='" & FORMAT ( ( _x2 - _x3 ), "0.0", "en-US" ) & "' height='22' rx='6' fill='{{LOSS3}}'/>"
        & "<text x='900' y='87' text-anchor='end' font-weight='700' fill='{{LOSS}}'>" & FORMAT ( _ot, "$#,0;-$#,0", "en-US" ) & "</text>"
        & "<text x='0' y='121' font-weight='700' fill='{{INK}}'>Net P&amp;L</text><rect x='" & FORMAT ( MIN ( _z, _x3 ), "0.0", "en-US" ) & "' y='106' width='" & FORMAT ( ABS ( _z - _x3 ), "0.0", "en-US" ) & "' height='22' rx='6' fill='{{INK}}'/>"
        & "<text x='900' y='121' text-anchor='end' font-weight='700' fill='{{INK}}'>" & FORMAT ( _net, "$#,0;-$#,0", "en-US" ) & "</text>"
        & "</svg>"
{SVG_END}""").replace("VAR _X = ( v ) => 0   -- placeholder, Power BI does not support lambdas; see inline math below\n", "").replace("VAR _row = ( 0 )\n", ""))

m(S, "SVG - Crypto vs Equity Weekly", col(f"""
-- cumulative P&L by week for crypto (green) and equity (red)
VAR _wk = FILTER ( ALLSELECTED ( gold_dim_date[WeekStart] ), NOT ISBLANK ( [Net P&L] ) )
VAR _t = ADDCOLUMNS ( _wk,
    "@c", VAR w = gold_dim_date[WeekStart] RETURN CALCULATE ( [Crypto P&L], FILTER ( ALLSELECTED ( gold_dim_date ), gold_dim_date[WeekStart] <= w ) ),
    "@e", VAR w = gold_dim_date[WeekStart] RETURN CALCULATE ( [Equity P&L], FILTER ( ALLSELECTED ( gold_dim_date ), gold_dim_date[WeekStart] <= w ) ) )
VAR _n = COUNTROWS ( _t )
VAR _hi = MAX ( 1, MAX ( MAXX ( _t, [@c] ), MAXX ( _t, [@e] ) ) )
VAR _lo = MIN ( 0, MIN ( MINX ( _t, [@c] ), MINX ( _t, [@e] ) ) )
VAR _r = ADDCOLUMNS ( _t, "@i", RANKX ( _t, gold_dim_date[WeekStart], , ASC ) )
VAR _P = ( 0 )
VAR _lc = CONCATENATEX ( _r, FORMAT ( 10 + ( [@i] - 1 ) / MAX ( 1, _n - 1 ) * 700, "0.0", "en-US" ) & "," & FORMAT ( 10 + ( _hi - [@c] ) / ( _hi - _lo ) * 140, "0.0", "en-US" ), " ", [@i], ASC )
VAR _le = CONCATENATEX ( _r, FORMAT ( 10 + ( [@i] - 1 ) / MAX ( 1, _n - 1 ) * 700, "0.0", "en-US" ) & "," & FORMAT ( 10 + ( _hi - [@e] ) / ( _hi - _lo ) * 140, "0.0", "en-US" ), " ", [@i], ASC )
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 820 160' font-family='Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif'>"
        & "<polyline points='" & _lc & "' fill='none' stroke='{{LEAF}}' stroke-width='2.5'/>"
        & "<polyline points='" & _le & "' fill='none' stroke='{{LOSS}}' stroke-width='2.5'/>"
        & "<text x='720' y='20' font-size='13' font-weight='700' fill='{{LEAF}}'>Crypto " & FORMAT ( [Crypto P&L], "+$#,0;-$#,0", "en-US" ) & "</text>"
        & "<text x='720' y='40' font-size='13' font-weight='700' fill='{{LOSS}}'>Equity " & FORMAT ( [Equity P&L], "+$#,0;-$#,0", "en-US" ) & "</text>"
        & "<text x='720' y='60' font-size='13' font-weight='700' fill='{{LOSS3}}'>Options " & FORMAT ( [Options P&L], "+$#,0;-$#,0", "en-US" ) & "</text>"
        & "</svg>"
{SVG_END}""").replace("VAR _P = ( 0 )\n", ""))

m(S, "SVG - Strategy Lollipop", col(f"""
-- 4 best and 4 worst strategies, stem from $0, dot size = number of trades
VAR _all = ADDCOLUMNS ( ALLSELECTED ( gold_fact_trades[strategy] ), "@v", [Net P&L], "@n", [Trades] )
VAR _sel = UNION ( TOPN ( 4, _all, [@v], DESC ), TOPN ( 4, _all, [@v], ASC ) )
VAR _rk = ADDCOLUMNS ( _sel, "@i", RANKX ( _sel, [@v], , DESC, DENSE ) )
VAR _m = MAX ( MAXX ( _sel, ABS ( [@v] ) ), 1 )
VAR _maxn = MAXX ( _sel, [@n] )
VAR _z = 590
VAR _rows = CONCATENATEX ( _rk,
    VAR y = FORMAT ( 14 + ( [@i] - 1 ) * 24.5, "0.0", "en-US" )
    VAR yt = FORMAT ( 18 + ( [@i] - 1 ) * 24.5, "0.0", "en-US" )
    VAR x = _z + [@v] / _m * 320
    VAR c = IF ( [@v] >= 0, "{{LEAF6}}", "{{LOSS}}" )
    RETURN
        "<text x='0' y='" & yt & "' font-family='Geist Mono,Consolas,Menlo,monospace' font-size='12' fill='{{INK}}'>" & gold_fact_trades[strategy] & "</text>"
        & "<line x1='" & FORMAT ( _z, "0.0", "en-US" ) & "' x2='" & FORMAT ( x, "0.0", "en-US" ) & "' y1='" & y & "' y2='" & y & "' stroke='" & c & "' stroke-width='2'/>"
        & "<circle cx='" & FORMAT ( x, "0.0", "en-US" ) & "' cy='" & y & "' r='" & FORMAT ( 5 + 7 * SQRT ( [@n] / _maxn ), "0.0", "en-US" ) & "' fill='" & c & "' stroke='#fff' stroke-width='1.5'/>"
        & "<text x='" & FORMAT ( x + IF ( [@v] >= 0, 16, -16 ), "0.0", "en-US" ) & "' y='" & yt & "' font-size='12' font-weight='700' fill='" & c & "' text-anchor='" & IF ( [@v] >= 0, "start", "end" ) & "'>" & FORMAT ( [@v], "+$#,0;-$#,0", "en-US" ) & "</text>"
        & "<text x='900' y='" & yt & "' font-size='11' fill='{{MUT}}' text-anchor='end'>" & [@n] & " trades</text>",
    "", [@i], ASC )
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 900 214' font-family='Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif'>"
        & "<line x1='" & FORMAT ( _z, "0.0", "en-US" ) & "' x2='" & FORMAT ( _z, "0.0", "en-US" ) & "' y1='0' y2='200' stroke='#BFC8C0'/>" & _rows & "</svg>"
{SVG_END}"""))

m(S, "SVG - R-Multiple Dots", col(f"""
-- every dot is a trade, binned to the nearest 0.5R (clamped to -2.5R … +3R)
VAR _tr = ADDCOLUMNS (
    FILTER ( ALLSELECTED ( gold_fact_trades ), NOT ISBLANK ( gold_fact_trades[r] ) ),
    "@b", MIN ( 3, MAX ( -2.5, ROUND ( gold_fact_trades[r] * 2, 0 ) / 2 ) ) )
VAR _bins = SELECTCOLUMNS ( GENERATESERIES ( -5, 6, 1 ), "@bin", [Value] / 2 )
VAR _cnt = ADDCOLUMNS ( _bins, "@n", VAR b = [@bin] RETURN COUNTROWS ( FILTER ( _tr, [@b] = b ) ) + 0 )
VAR _cols = CONCATENATEX ( _cnt,
    VAR b = [@bin]  VAR n = [@n]
    VAR cx = 40 + ( b + 2.5 ) * 2 * 72
    VAR c = IF ( b < 0, "{{LOSS}}", IF ( b = 0, "#BFC8C0", "{{LEAF6}}" ) )
    VAR dots = CONCATENATEX ( GENERATESERIES ( 0, MAX ( 0, n - 1 ), 1 ),
        IF ( n > 0,
            "<circle cx='" & FORMAT ( cx - 15 + MOD ( [Value], 4 ) * 10, "0", "en-US" ) & "' cy='" & ( 180 - INT ( [Value] / 4 ) * 10 ) & "' r='4' fill='" & c & "'/>" ), "" )
    RETURN dots
        & "<text x='" & cx & "' y='" & ( 168 - INT ( MAX ( n - 1, 0 ) / 4 ) * 10 - 10 ) & "' font-size='10' font-weight='700' text-anchor='middle' fill='{{INK}}'>" & n & "</text>"
        & "<text x='" & cx & "' y='202' font-size='10' text-anchor='middle' fill='{{MUT}}'>" & FORMAT ( b, "+0.0;-0.0;0", "en-US" ) & "R" & "</text>",
    "", [@bin], ASC )
VAR _svg = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 900 210' font-family='Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif'>"
        & "<line x1='0' x2='900' y1='188' y2='188' stroke='{{HAIR}}'/>" & _cols & "</svg>"
{SVG_END}"""))

m(S, "SVG - Long vs Short Units", col(f"""
-- one tick per trade: wins green, losses red, for shorts and longs
VAR _row = ( 0 )
VAR _sw = CALCULATE ( [Wins], KEEPFILTERS ( gold_fact_trades[side] = "short" ) )
VAR _sl = [Short Trades] - _sw
VAR _lw = CALCULATE ( [Wins], KEEPFILTERS ( gold_fact_trades[side] = "long" ) )
VAR _ll = [Long Trades] - _lw
VAR _u = 3.1
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 900 90' font-family='Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif' font-size='13'>"
        & "<text x='0' y='22' fill='#fff' font-weight='700'>Short</text>"
        & "<rect x='70' y='10' width='" & FORMAT ( _sw * _u, "0.0", "en-US" ) & "' height='16' fill='{{LEAF}}'/>"
        & "<rect x='" & FORMAT ( 70 + _sw * _u, "0.0", "en-US" ) & "' y='10' width='" & FORMAT ( _sl * _u, "0.0", "en-US" ) & "' height='16' fill='{{LOSS}}'/>"
        & "<text x='70' y='42' font-size='11' fill='rgba(255,255,255,.6)'>" & _sw & " won · " & _sl & " lost</text>"
        & "<text x='0' y='66' fill='#fff' font-weight='700'>Long</text>"
        & "<rect x='70' y='54' width='" & FORMAT ( _lw * _u, "0.0", "en-US" ) & "' height='16' fill='{{LEAF}}'/>"
        & "<rect x='" & FORMAT ( 70 + _lw * _u, "0.0", "en-US" ) & "' y='54' width='" & FORMAT ( _ll * _u, "0.0", "en-US" ) & "' height='16' fill='{{LOSS}}'/>"
        & "<text x='70' y='86' font-size='11' fill='rgba(255,255,255,.6)'>" & _lw & " won · " & _ll & " lost</text>"
        & "</svg>"
{SVG_END}""").replace("VAR _row = ( 0 )\n", ""))

m(S, "SVG - Positions Treemap", col(f"""
-- strip treemap: width = market value, colour = return on cost
VAR _p = ADDCOLUMNS ( VALUES ( gold_fact_positions[symbol] ), "@mv", [Position Market Value], "@r", [Position Return %] )
VAR _tot = SUMX ( _p, [@mv] )
VAR _rk = ADDCOLUMNS ( _p, "@i", RANKX ( _p, [@mv], , DESC, DENSE ) )
VAR _x = ADDCOLUMNS ( _rk, "@x0", VAR i = [@i] RETURN SUMX ( FILTER ( _rk, [@i] < i ), [@mv] ) / _tot * 900 )
VAR _tiles = CONCATENATEX ( _x,
    VAR w = [@mv] / _tot * 900
    VAR c = IF ( [@r] >= 0.01, "{{LEAF6}}", IF ( [@r] >= 0, "{{LEAF3}}", IF ( [@r] > -0.01, "{{LOSS3}}", "{{LOSS}}" ) ) )
    VAR tc = IF ( ABS ( [@r] ) >= 0.01, "#fff", "{{INK}}" )
    RETURN
        "<rect x='" & FORMAT ( [@x0] + 1, "0.0", "en-US" ) & "' y='0' width='" & FORMAT ( MAX ( w - 2, 1 ), "0.0", "en-US" ) & "' height='120' rx='6' fill='" & c & "'/>"
        & IF ( w > 40,
            "<text x='" & FORMAT ( [@x0] + 8, "0.0", "en-US" ) & "' y='18' font-size='12' font-weight='800' fill='" & tc & "'>" & gold_fact_positions[symbol] & "</text>"
            & "<text x='" & FORMAT ( [@x0] + 8, "0.0", "en-US" ) & "' y='110' font-size='12' font-weight='700' fill='" & tc & "'>" & FORMAT ( [@r], "+0.00%;-0.00%", "en-US" ) & "</text>" ),
    "", [@i], ASC )
VAR _svg = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 900 120' font-family='Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif'>" & _tiles & "</svg>"
{SVG_END}"""))

m(S, "SVG - Order Flow Sankey", col(f"""
-- all orders → side → outcome; ribbon width = order count
VAR _o = ADDCOLUMNS ( ALLSELECTED ( gold_fact_orders[side], gold_fact_orders[status] ), "@n", CALCULATE ( [Orders] ) )
VAR _f = ADDCOLUMNS ( FILTER ( _o, [@n] > 0 ),
    "@s", SWITCH ( LOWER ( gold_fact_orders[side] ), "buy", 1, "sell", 2, 3 ),
    "@g", SWITCH ( LOWER ( gold_fact_orders[status] ), "filled", 1, "canceled", 2, "expired", 3, 4 ) )
VAR _flows = GROUPBY ( _f, [@s], [@g], "@n", SUMX ( CURRENTGROUP (), [@n] ) )
VAR _tot = SUMX ( _flows, [@n] )
VAR _k = 180 / _tot          -- px per order
VAR _gap = 10
VAR _so = ADDCOLUMNS ( _flows,
    "@sy", VAR s = [@s] VAR g = [@g]
           RETURN 10 + ( s - 1 ) * _gap + SUMX ( FILTER ( _flows, [@s] < s || ( [@s] = s && [@g] < g ) ), [@n] ) * _k,
    "@ty", VAR s = [@s] VAR g = [@g]
           RETURN 10 + ( g - 1 ) * _gap + SUMX ( FILTER ( _flows, [@g] < g || ( [@g] = g && [@s] < s ) ), [@n] ) * _k )
VAR _ribbons = CONCATENATEX ( _so,
    VAR h = [@n] * _k
    VAR c = SWITCH ( [@g], 1, "{{LEAF6}}", 2, "#BFC8C0", 3, "{{LOSS}}", "{{LOSS3}}" )
    RETURN "<path d='M300," & FORMAT ( [@sy], "0.0", "en-US" ) & " C450," & FORMAT ( [@sy], "0.0", "en-US" ) & " 450," & FORMAT ( [@ty], "0.0", "en-US" ) & " 600," & FORMAT ( [@ty], "0.0", "en-US" )
        & " L600," & FORMAT ( [@ty] + h, "0.0", "en-US" ) & " C450," & FORMAT ( [@ty] + h, "0.0", "en-US" ) & " 450," & FORMAT ( [@sy] + h, "0.0", "en-US" ) & " 300," & FORMAT ( [@sy] + h, "0.0", "en-US" ) & " Z' fill='" & c & "' fill-opacity='.45'/>",
    "" )
VAR _sideN = ( s ) => 0
VAR _nodes =
    CONCATENATEX ( GROUPBY ( _so, [@s] ),
        VAR s = [@s] VAR n = SUMX ( FILTER ( _flows, [@s] = s ), [@n] )
        VAR y = MINX ( FILTER ( _so, [@s] = s ), [@sy] )
        RETURN "<rect x='292' y='" & FORMAT ( y, "0.0", "en-US" ) & "' width='8' height='" & FORMAT ( n * _k, "0.0", "en-US" ) & "' fill='{{INK}}'/>"
            & "<text x='286' y='" & FORMAT ( y + n * _k / 2 + 4, "0.0", "en-US" ) & "' font-size='11' text-anchor='end' fill='{{INK}}'>" & SWITCH ( s, 1, "Buy", 2, "Sell", "Other" ) & " " & n & "</text>", "" )
    & CONCATENATEX ( GROUPBY ( _so, [@g] ),
        VAR g = [@g] VAR n = SUMX ( FILTER ( _flows, [@g] = g ), [@n] )
        VAR y = MINX ( FILTER ( _so, [@g] = g ), [@ty] )
        RETURN "<rect x='600' y='" & FORMAT ( y, "0.0", "en-US" ) & "' width='8' height='" & FORMAT ( n * _k, "0.0", "en-US" ) & "' fill='" & SWITCH ( g, 1, "{{LEAF6}}", 2, "#9AA39C", 3, "{{LOSS}}", "{{LOSS3}}" ) & "'/>"
            & "<text x='616' y='" & FORMAT ( y + n * _k / 2 + 4, "0.0", "en-US" ) & "' font-size='11' fill='{{INK}}'>" & SWITCH ( g, 1, "Filled", 2, "Canceled", 3, "Expired", "Working" ) & " " & n
            & " (" & FORMAT ( n / _tot, "0%" ) & ")</text>", "" )
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 760 240' font-family='Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif'>"
        & "<rect x='150' y='10' width='8' height='" & FORMAT ( 180 + 2 * _gap, "0", "en-US" ) & "' fill='{{INK}}'/>"
        & "<text x='140' y='110' font-size='18' font-weight='800' text-anchor='end' fill='{{INK}}'>" & _tot & "</text>"
        & "<text x='140' y='126' font-size='10' text-anchor='end' fill='{{MUT}}'>orders</text>"
        & _ribbons & _nodes & "</svg>"
{SVG_END}""").replace("VAR _sideN = ( s ) => 0\n", ""))

m(S, "SVG - Cash Donut", col(f"""
VAR _p = [Capital Deployed %]
VAR _r = 40  VAR _c = 2 * PI () * _r
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' font-family='Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif'>"
        & "<circle cx='50' cy='50' r='40' fill='none' stroke='{{HAIR}}' stroke-width='9'/>"
        & "<circle cx='50' cy='50' r='40' fill='none' stroke='{{LEAF6}}' stroke-width='9' stroke-linecap='round'"
        & " stroke-dasharray='" & FORMAT ( _p * _c, "0.0", "en-US" ) & " " & FORMAT ( _c, "0.0", "en-US" ) & "' transform='rotate(-90 50 50)'/>"
        & "<text x='50' y='54' font-size='16' font-weight='800' text-anchor='middle' fill='{{INK}}'>" & FORMAT ( _p, "0%" ) & "</text>"
        & "<text x='50' y='66' font-size='6' text-anchor='middle' fill='{{MUT}}'>INVESTED</text></svg>"
{SVG_END}"""))

m(S, "SVG - Market Coverage", col(f"""
VAR _eq = DIVIDE ( [Equities Priced], [Equities Tracked] )
VAR _cr = DIVIDE ( [Crypto Priced], [Crypto Pairs Tracked] )
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 400 60' font-family='Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif' font-size='11'>"
        & "<text x='0' y='14' fill='#fff' font-weight='700'>Equities</text>"
        & "<rect x='80' y='6' width='260' height='8' rx='4' fill='rgba(255,255,255,.12)'/><rect x='80' y='6' width='" & FORMAT ( 260 * _eq, "0", "en-US" ) & "' height='8' rx='4' fill='{{LEAF}}'/>"
        & "<text x='400' y='14' text-anchor='end' fill='{{LEAF}}' font-weight='700'>" & [Equities Priced] & "/" & [Equities Tracked] & "</text>"
        & "<text x='0' y='44' fill='#fff' font-weight='700'>Crypto</text>"
        & "<rect x='80' y='36' width='260' height='8' rx='4' fill='rgba(255,255,255,.12)'/><rect x='80' y='36' width='" & FORMAT ( 260 * _cr, "0", "en-US" ) & "' height='8' rx='4' fill='{{LOSS}}'/>"
        & "<text x='400' y='44' text-anchor='end' fill='{{LOSS}}' font-weight='700'>" & [Crypto Priced] & "/" & [Crypto Pairs Tracked] & "</text>"
        & "</svg>"
{SVG_END}"""))

# ───────────────────────── 07 · page 1 layout (framed SVGs sized to their slot) ─────────────────────────
# Page grid (1920 x 1080): rail 0-72 · content x 96..1888 · header y24 h96 · KPIs y140 h170
# row 2 y334 h340 · row 3 y698 h358 · half-width cards 884 wide at x 96 / 1004
L1 = "07-page1-layout"
RAW = lambda m_: f'SUBSTITUTE ( SUBSTITUTE ( MID ( [{m_}], 25, 100000 ), "%23", "#" ), "%25", "%" )'   # strip data-URI prefix

def framed(name, inner, w, h, title_expr, sub_expr, dark=False, extra="\"\"", inner_box=(28, 88, None, None)):
    bg = C["INK"] if dark else "#FFFFFF"
    tc = "#FFFFFF" if dark else C["INK"]
    mc = "rgba(255,255,255,.6)" if dark else C["MUT"]
    ix, iy, iw, ih = inner_box
    iw = iw or w - 2 * ix
    ih = ih or h - iy - 20
    m(L1, name, f"""
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' font-family='Plus Jakarta Sans,Segoe UI,sans-serif'>"
        & "<rect width='{w}' height='{h}' rx='22' fill='{bg}'/>"
        & "<text x='28' y='42' font-size='20' font-weight='700' fill='{tc}'>" & {title_expr} & "</text>"
        & "<text x='28' y='64' font-size='12' fill='{mc}'>" & {sub_expr} & "</text>"
        & {extra}
        & "<svg x='{ix}' y='{iy}' width='{iw}' height='{ih}'>" & {RAW(inner)} & "</svg>"
        & "</svg>"
{SVG_END}""")

def pill(x, y, w, text_expr, bg, fg, h=26):
    return (f'"<rect x=\'{x}\' y=\'{y}\' width=\'{w}\' height=\'{h}\' rx=\'{h//2}\' fill=\'{bg}\'/>'
            f'<text x=\'{x + w/2}\' y=\'{y + h/2 + 4}\' font-size=\'12\' font-weight=\'700\' text-anchor=\'middle\' fill=\'{fg}\'>" & {text_expr} & "</text>"')

framed("SVG - Card Equity Curve", "SVG - Equity Curve & Drawdown", 884, 340,
       '"Equity curve &amp; drawdown"', '"Cumulative closed P&amp;L by day · shaded = distance below the running peak"',
       extra=pill(704, 22, 66, '"Daily"', C["INK"], "#FFFFFF") + ' & ' + pill(776, 22, 80, '"Weekly"', "#FFFFFF", C["MUT"]))
framed("SVG - Card Waterfall", "SVG - P&L Waterfall", 884, 358,
       "[Title - The Book]", '"P&amp;L waterfall · stop exits alone erase more than half of all gains"',
       extra=pill(686, 22, 170, '"Stops = " & FORMAT ( [Stop Share of Gains], "0%" ) & " of gains"', "#FDE7E4", "#C2453A"),
       inner_box=(28, 100, None, 230))
m(L1, "SVG - Card Crypto", col(f"""
-- dark card: weekly cumulative lines + one bar per asset class
VAR _c = [Crypto P&L]  VAR _e = [Equity P&L]  VAR _o = [Options P&L]
VAR _mx = MAX ( ABS ( _c ), MAX ( ABS ( _e ), ABS ( _o ) ) )
VAR _bar = 560
VAR _row = ( 0 )
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 884 358' font-family='Plus Jakarta Sans,Segoe UI,sans-serif'>"
        & "<rect width='884' height='358' rx='22' fill='{{INK}}'/>"
        & "<text x='28' y='42' font-size='20' font-weight='700' fill='#FFFFFF'>" & IF ( _c > MAX ( _e, _o ), "Only crypto pays", "Crypto is not the winner" ) & "</text>"
        & "<text x='28' y='64' font-size='12' fill='rgba(255,255,255,.6)'>Cumulative P&amp;L by week</text>"
        & "<rect x='776' y='22' width='80' height='26' rx='13' fill='#FFFFFF'/><text x='816' y='39' font-size='12' font-weight='700' text-anchor='middle' fill='{{INK}}'>By asset</text>"
        & "<svg x='28' y='76' width='828' height='178'>" & {RAW("SVG - Crypto vs Equity Weekly")} & "</svg>"
        & "<text x='28' y='276' font-size='12' font-weight='700' fill='#FFFFFF'>Crypto</text>"
        & "<rect x='110' y='268' width='" & FORMAT ( _bar * ABS ( _c ) / _mx, "0.0", "en-US" ) & "' height='9' rx='4.5' fill='{{LEAF}}'/>"
        & "<text x='856' y='276' font-size='12' font-weight='700' text-anchor='end' fill='{{LEAF}}'>" & FORMAT ( _c, "+$#,0;-$#,0", "en-US" ) & "</text>"
        & "<text x='28' y='298' font-size='12' font-weight='700' fill='#FFFFFF'>Equity</text>"
        & "<rect x='110' y='290' width='" & FORMAT ( _bar * ABS ( _e ) / _mx, "0.0", "en-US" ) & "' height='9' rx='4.5' fill='{{LOSS}}'/>"
        & "<text x='856' y='298' font-size='12' font-weight='700' text-anchor='end' fill='{{LOSS}}'>" & FORMAT ( _e, "+$#,0;-$#,0", "en-US" ) & "</text>"
        & "<text x='28' y='320' font-size='12' font-weight='700' fill='#FFFFFF'>Options</text>"
        & "<rect x='110' y='312' width='" & FORMAT ( _bar * ABS ( _o ) / _mx, "0.0", "en-US" ) & "' height='9' rx='4.5' fill='{{LOSS}}'/>"
        & "<text x='856' y='320' font-size='12' font-weight='700' text-anchor='end' fill='{{LOSS}}'>" & FORMAT ( _o, "+$#,0;-$#,0", "en-US" ) & "</text>"
        & "<text x='28' y='344' font-size='11' fill='rgba(255,255,255,.55)'>" & FORMAT ( [Crypto Trades], "#,0" ) & " crypto trades · " & FORMAT ( [Crypto Win Rate], "0%" ) & " win · PF " & FORMAT ( [Crypto Profit Factor], "0.00", "en-US" ) & "</text>"
        & "</svg>"
{SVG_END}""").replace("VAR _row = ( 0 )\n", ""))

m(L1, "SVG - Header The Book", col(f"""
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1792 96' font-family='Plus Jakarta Sans,Segoe UI,sans-serif'>"
        & "<text x='0' y='46' font-size='38' font-weight='800' letter-spacing='-1' fill='{{INK}}'>The Book</text>"
        & "<text x='2' y='78' font-size='15' fill='{{MUT}}'>" & [Subtitle - The Book] & "</text>"
        & "<rect x='1320' y='26' width='170' height='42' rx='21' fill='#FFFFFF' stroke='{{HAIR}}'/>"
        & "<circle cx='1344' cy='47' r='5' fill='{{LEAF}}'/><text x='1358' y='52' font-size='14' font-weight='600' fill='{{INK}}'>Alpaca · Paper</text>"
        & "<rect x='1502' y='26' width='150' height='42' rx='21' fill='{{INK}}'/><text x='1520' y='52' font-size='14' font-weight='600' fill='#FFFFFF'>Last 10 weeks  ⌄</text>"
        & "<rect x='1664' y='26' width='128' height='42' rx='21' fill='{{INK}}'/><text x='1682' y='52' font-size='14' font-weight='600' fill='#FFFFFF'>All assets  ⌄</text>"
        & "</svg>"
{SVG_END}"""))

m(L1, "SVG - Rail", col(f"""
-- left navigation rail (page 1 active)
VAR _active = 1
VAR _item = "<g font-size='11' text-anchor='middle'>"
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 72 1080' font-family='Plus Jakarta Sans,Segoe UI,sans-serif'>"
        & "<rect width='72' height='1080' fill='{{INK}}'/>"
        & "<rect x='14' y='24' width='44' height='44' rx='12' fill='{{LEAF}}'/>"
        & "<polyline points='24,54 32,44 40,50 49,38' fill='none' stroke='{{INK}}' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/>"
        & _item
        & "<polyline points='26,140 32,132 38,136 46,126' fill='none' stroke='" & IF ( _active = 1, "#FFFFFF", "rgba(255,255,255,.5)" ) & "' stroke-width='2'/>"
        & "<line x1='26' y1='144' x2='46' y2='144' stroke='" & IF ( _active = 1, "#FFFFFF", "rgba(255,255,255,.5)" ) & "' stroke-width='2'/>"
        & "<text x='36' y='164' fill='" & IF ( _active = 1, "#FFFFFF", "rgba(255,255,255,.5)" ) & "'>Book</text>"
        & "<circle cx='36' cy='212' r='10' fill='none' stroke='" & IF ( _active = 2, "#FFFFFF", "rgba(255,255,255,.5)" ) & "' stroke-width='2'/>"
        & "<circle cx='36' cy='212' r='4' fill='none' stroke='" & IF ( _active = 2, "#FFFFFF", "rgba(255,255,255,.5)" ) & "' stroke-width='2'/>"
        & "<text x='36' y='240' fill='" & IF ( _active = 2, "#FFFFFF", "rgba(255,255,255,.5)" ) & "'>Edge</text>"
        & "<rect x='26' y='278' width='20' height='16' rx='3' fill='none' stroke='" & IF ( _active = 3, "#FFFFFF", "rgba(255,255,255,.5)" ) & "' stroke-width='2'/>"
        & "<line x1='26' y1='285' x2='46' y2='285' stroke='" & IF ( _active = 3, "#FFFFFF", "rgba(255,255,255,.5)" ) & "' stroke-width='2'/>"
        & "<text x='36' y='314' fill='" & IF ( _active = 3, "#FFFFFF", "rgba(255,255,255,.5)" ) & "'>Desk</text>"
        & "<circle cx='36' cy='1030' r='5' fill='{{LEAF}}'/>"
        & "<text x='36' y='1054' font-size='9' font-weight='700' letter-spacing='1' fill='rgba(255,255,255,.6)'>PAPER</text>"
        & "</g></svg>"
{SVG_END}"""))

# ───────────────────────── 08 · page 2 layout (The Edge) ─────────────────────────
L2 = "08-page2-layout"
_rail = next(e for f_, n_, fm_, e in M if n_ == "SVG - Rail")
for _name, _active in [("SVG - Rail The Edge", 2), ("SVG - Rail The Desk", 3)]:
    m(L2 if _active == 2 else "09-page3-layout", _name,
      _rail.replace("(page 1 active)", f"(page {_active} active)").replace("VAR _active = 1", f"VAR _active = {_active}"))

m(L2, "SVG - Header The Edge", col(f"""
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1792 96' font-family='Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif'>"
        & "<text x='0' y='46' font-size='38' font-weight='800' letter-spacing='-1' fill='{{INK}}'>The Edge</text>"
        & "<text x='2' y='78' font-size='15' fill='{{MUT}}'>Where do the wins and losses come from? · R-multiples · exits · " & FORMAT ( [Strategies], "0" ) & " strategies</text>"
        & "<rect x='1290' y='26' width='170' height='42' rx='21' fill='#FFFFFF' stroke='{{HAIR}}'/>"
        & "<circle cx='1314' cy='47' r='5' fill='{{LEAF}}'/><text x='1328' y='52' font-size='14' font-weight='600' fill='{{INK}}'>Alpaca · Paper</text>"
        & "<rect x='1472' y='26' width='150' height='42' rx='21' fill='{{INK}}'/><text x='1490' y='52' font-size='14' font-weight='600' fill='#FFFFFF'>Last 10 weeks  ⌄</text>"
        & "<rect x='1634' y='26' width='158' height='42' rx='21' fill='{{INK}}'/><text x='1652' y='52' font-size='14' font-weight='600' fill='#FFFFFF'>All strategies  ⌄</text>"
        & "</svg>"
{SVG_END}"""))

def framed2(name, inner, w, h, title_expr, sub_expr, extra='""', inner_box=(28, 88, None, None)):
    ix, iy, iw, ih = inner_box
    iw = iw or w - 2 * ix
    ih = ih or h - iy - 20
    m(L2, name, f"""
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' font-family='Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif'>"
        & "<rect width='{w}' height='{h}' rx='22' fill='#FFFFFF'/>"
        & "<text x='28' y='42' font-size='20' font-weight='700' fill='{C["INK"]}'>" & {title_expr} & "</text>"
        & "<text x='28' y='64' font-size='12' fill='{C["MUT"]}'>" & {sub_expr} & "</text>"
        & {extra}
        & "<svg x='{ix}' y='{iy}' width='{iw}' height='{ih}'>" & {RAW(inner)} & "</svg>"
        & "</svg>"
{SVG_END}""")

framed2("SVG - Card Strategy Lollipop", "SVG - Strategy Lollipop", 884, 340,
        '"Tagged setups earn · untagged legacy bleeds"',
        '"Net P&amp;L of the 4 best and 4 worst of " & FORMAT ( [Strategies], "0" ) & " strategies · dot size = number of trades"',
        extra=pill(726, 22, 130, '"4 best · 4 worst"', "#EEF2EE", C["MUT"]), inner_box=(28, 92, None, 228))
framed2("SVG - Card R-Multiple Dots", "SVG - R-Multiple Dots", 884, 358,
        '"Every dot is a trade · losses pile up past the stop"',
        '"Trades with a defined stop, grouped by R-multiple (net P&amp;L ÷ planned risk)"',
        extra=pill(686, 22, 170, 'FORMAT ( [Lost Past -1R Trades], "0" ) & " slipped the stop"', "#FDE7E4", "#C2453A"),
        inner_box=(28, 92, None, 246))

m(L2, "SVG - Card Shorts vs Longs", col(f"""
-- dark card: short vs long scorecards + one tick per trade
VAR _sp = [Short P&L]  VAR _lp = [Long P&L]
VAR _box = ( 0 )
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 884 358' font-family='Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif'>"
        & "<rect width='884' height='358' rx='22' fill='{{INK}}'/>"
        & "<text x='28' y='42' font-size='20' font-weight='700' fill='#FFFFFF'>" & IF ( _sp > _lp, "Shorts carry the book", "Longs carry the book" ) & "</text>"
        & "<text x='28' y='64' font-size='12' fill='rgba(255,255,255,.6)'>Net P&amp;L and win rate by side</text>"
        & "<rect x='776' y='22' width='80' height='26' rx='13' fill='#FFFFFF'/><text x='816' y='39' font-size='12' font-weight='700' text-anchor='middle' fill='{{INK}}'>By side</text>"
        & "<rect x='28' y='84' width='404' height='104' rx='16' fill='{{DARK2}}'/>"
        & "<text x='48' y='112' font-size='12' fill='rgba(255,255,255,.6)'>Short · " & FORMAT ( [Short Trades], "0" ) & "</text>"
        & "<text x='48' y='152' font-size='34' font-weight='800' fill='" & IF ( _sp >= 0, "{{LEAF}}", "{{LOSS}}" ) & "'>" & FORMAT ( _sp, "+$#,0;-$#,0", "en-US" ) & "</text>"
        & "<text x='48' y='174' font-size='12' fill='rgba(255,255,255,.6)'>" & FORMAT ( [Short Win Rate], "0%" ) & " win</text>"
        & "<rect x='452' y='84' width='404' height='104' rx='16' fill='{{DARK2}}'/>"
        & "<text x='472' y='112' font-size='12' fill='rgba(255,255,255,.6)'>Long · " & FORMAT ( [Long Trades], "0" ) & "</text>"
        & "<text x='472' y='152' font-size='34' font-weight='800' fill='" & IF ( _lp >= 0, "{{LEAF}}", "{{LOSS}}" ) & "'>" & FORMAT ( _lp, "+$#,0;-$#,0", "en-US" ) & "</text>"
        & "<text x='472' y='174' font-size='12' fill='rgba(255,255,255,.6)'>" & FORMAT ( [Long Win Rate], "0%" ) & " win</text>"
        & "<svg x='28' y='206' width='828' height='104'>" & {RAW("SVG - Long vs Short Units")} & "</svg>"
        & "<text x='28' y='338' font-size='11' fill='rgba(255,255,255,.55)'>" & FORMAT ( [Long Share of Trades], "0%" ) & " of trades are long — " & IF ( _lp < _sp, "the losing side", "the winning side" ) & "</text>"
        & "</svg>"
{SVG_END}""").replace("VAR _box = ( 0 )\n", ""))

# ───────────────────────── 09 · page 3 layout (The Desk) ─────────────────────────
L3 = "09-page3-layout"
m(L3, "SVG - Header The Desk", col(f"""
VAR _asof = CALCULATE ( MAX ( gold_fact_account[Date] ), REMOVEFILTERS ( gold_dim_date ) )
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1792 96' font-family='Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif'>"
        & "<text x='0' y='46' font-size='38' font-weight='800' letter-spacing='-1' fill='{{INK}}'>The Desk</text>"
        & "<text x='2' y='78' font-size='15' fill='{{MUT}}'>What is open right now? · positions · cash · order flow — as of " & FORMAT ( _asof, "d mmm yyyy", "en-US" ) & "</text>"
        & "<rect x='1376' y='26' width='170' height='42' rx='21' fill='#FFFFFF' stroke='{{HAIR}}'/>"
        & "<circle cx='1400' cy='47' r='5' fill='{{LEAF}}'/><text x='1414' y='52' font-size='14' font-weight='600' fill='{{INK}}'>Alpaca · Paper</text>"
        & "<rect x='1558' y='26' width='96' height='42' rx='21' fill='{{INK}}'/><text x='1576' y='52' font-size='14' font-weight='600' fill='#FFFFFF'>Today  ⌄</text>"
        & "<rect x='1664' y='26' width='128' height='42' rx='21' fill='{{INK}}'/><text x='1682' y='52' font-size='14' font-weight='600' fill='#FFFFFF'>All assets  ⌄</text>"
        & "</svg>"
{SVG_END}"""))

m(L3, "SVG - Card Positions Treemap", col(f"""
-- strip treemap sized to the card: tile width = market value, colour = return on cost
VAR _p = ADDCOLUMNS ( VALUES ( gold_fact_positions[symbol] ), "@mv", [Position Market Value], "@r", [Position Return %] )
VAR _tot = SUMX ( _p, [@mv] )
VAR _rk = ADDCOLUMNS ( _p, "@i", RANKX ( _p, [@mv], , DESC, DENSE ) )
VAR _x = ADDCOLUMNS ( _rk, "@x0", VAR i = [@i] RETURN 28 + SUMX ( FILTER ( _rk, [@i] < i ), [@mv] ) / _tot * 828 )
VAR _tiles = CONCATENATEX ( _x,
    VAR w = [@mv] / _tot * 828
    VAR c = IF ( [@r] >= 0.01, "{{LEAF6}}", IF ( [@r] >= 0, "{{LEAF3}}", IF ( [@r] > -0.01, "{{LOSS3}}", "{{LOSS}}" ) ) )
    VAR tc = IF ( ABS ( [@r] ) >= 0.01, "#FFFFFF", "{{INK}}" )
    RETURN
        "<rect x='" & FORMAT ( [@x0] + 2, "0.0", "en-US" ) & "' y='96' width='" & FORMAT ( MAX ( w - 4, 1 ), "0.0", "en-US" ) & "' height='222' rx='10' fill='" & c & "'/>"
        & IF ( w > 44,
            "<text x='" & FORMAT ( [@x0] + 12, "0.0", "en-US" ) & "' y='120' font-size='14' font-weight='800' fill='" & tc & "'>" & gold_fact_positions[symbol] & "</text>"
            & "<text x='" & FORMAT ( [@x0] + 12, "0.0", "en-US" ) & "' y='137' font-size='10' fill='" & tc & "' fill-opacity='.8'>" & FORMAT ( [@mv], "$#,0", "en-US" ) & " · " & FORMAT ( DIVIDE ( [@mv], _tot ), "0%" ) & "</text>"
            & "<text x='" & FORMAT ( [@x0] + w - 10, "0.0", "en-US" ) & "' y='306' font-size='14' font-weight='800' text-anchor='end' fill='" & tc & "'>" & FORMAT ( [@r], "+0.00%;-0.00%", "en-US" ) & "</text>" ),
    "", [@i], ASC )
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 884 340' font-family='Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif'>"
        & "<rect width='884' height='340' rx='22' fill='#FFFFFF'/>"
        & "<text x='28' y='42' font-size='20' font-weight='700' fill='{{INK}}'>Open positions · " & IF ( [Top Position Share] >= 0.3, "one name carries the gain", "exposure is spread out" ) & "</text>"
        & "<text x='28' y='64' font-size='12' fill='{{MUT}}'>Tile area = market value · colour = return on cost · " & FORMAT ( [Open Positions], "0" ) & " open positions</text>"
        & "<rect x='700' y='30' width='14' height='10' rx='2' fill='{{LOSS}}'/><rect x='716' y='30' width='14' height='10' rx='2' fill='{{LOSS3}}'/>"
        & "<rect x='732' y='30' width='14' height='10' rx='2' fill='{{LEAF3}}'/><rect x='748' y='30' width='14' height='10' rx='2' fill='{{LEAF6}}'/>"
        & "<text x='770' y='39' font-size='11' fill='{{MUT}}'>−1% → +1%</text>"
        & _tiles & "</svg>"
{SVG_END}"""))

m(L3, "SVG - Card Order Flow", col(f"""
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 884 358' font-family='Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif'>"
        & "<rect width='884' height='358' rx='22' fill='#FFFFFF'/>"
        & "<text x='28' y='42' font-size='20' font-weight='700' fill='{{INK}}'>Where " & FORMAT ( [Orders], "#,0", "en-US" ) & " orders went</text>"
        & "<text x='28' y='64' font-size='12' fill='{{MUT}}'>Order flow: all orders → side → outcome · band width = order count</text>"
        & "<rect x='686' y='22' width='170' height='26' rx='13' fill='{{MINT}}'/><text x='771' y='39' font-size='12' font-weight='700' text-anchor='middle' fill='{{LEAF6}}'>" & FORMAT ( [Cancel Rate], "0%" ) & " cancelled · expected</text>"
        & "<svg x='28' y='88' width='828' height='252'>" & {RAW("SVG - Order Flow Sankey")} & "</svg>"
        & "</svg>"
{SVG_END}"""))

m(L3, "SVG - Card Market Coverage", col(f"""
-- dark card: price coverage bars + one chip per crypto base (green = has daily bars on Alpaca)
VAR _priced = CALCULATETABLE ( VALUES ( gold_fact_prices_daily[symbol] ), REMOVEFILTERS ( gold_dim_date ), gold_fact_prices_daily[asset_class] = "crypto" )
VAR _bases = ADDCOLUMNS ( CALCULATETABLE ( VALUES ( gold_dim_symbol[base] ), gold_dim_symbol[asset_class] = "crypto" ),
    "@ok", IF ( CONTAINS ( _priced, gold_fact_prices_daily[symbol], gold_dim_symbol[base] & "USD" ), 1, 0 ) )
VAR _n = COUNTROWS ( _bases )
VAR _ok = SUMX ( _bases, [@ok] )
VAR _rk = ADDCOLUMNS ( _bases, "@i", RANKX ( _bases, gold_dim_symbol[base], , ASC, DENSE ) - 1 )
VAR _chips = CONCATENATEX ( _rk,
    VAR cx = 28 + MOD ( [@i], 12 ) * 69
    VAR cy = 168 + INT ( [@i] / 12 ) * 30
    VAR c = IF ( [@ok] = 1, "{{LEAF}}", "{{LOSS}}" )
    RETURN "<rect x='" & cx & "' y='" & cy & "' width='62' height='22' rx='6' fill='none' stroke='" & c & "' stroke-opacity='.7'/>"
        & "<text x='" & ( cx + 31 ) & "' y='" & ( cy + 15 ) & "' font-size='10' font-weight='700' text-anchor='middle' fill='" & c & "'>" & LEFT ( gold_dim_symbol[base], 7 ) & "</text>",
    "", [@i], ASC )
VAR _eqw = 520 * DIVIDE ( [Equities Priced], [Equities Tracked] )
VAR _crw = 520 * DIVIDE ( _ok, _n )
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 884 358' font-family='Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif'>"
        & "<rect width='884' height='358' rx='22' fill='{{INK}}'/>"
        & "<text x='28' y='42' font-size='20' font-weight='700' fill='#FFFFFF'>Market coverage</text>"
        & "<text x='28' y='64' font-size='12' fill='rgba(255,255,255,.6)'>Symbols with daily price bars on Alpaca</text>"
        & "<rect x='756' y='22' width='100' height='26' rx='13' fill='#FFFFFF'/><text x='806' y='39' font-size='12' font-weight='700' text-anchor='middle' fill='{{INK}}'>Daily bars</text>"
        & "<text x='28' y='104' font-size='13' font-weight='700' fill='#FFFFFF'>Equities</text>"
        & "<rect x='130' y='96' width='520' height='9' rx='4.5' fill='rgba(255,255,255,.12)'/><rect x='130' y='96' width='" & FORMAT ( _eqw, "0", "en-US" ) & "' height='9' rx='4.5' fill='{{LEAF}}'/>"
        & "<text x='856' y='104' font-size='13' font-weight='700' text-anchor='end' fill='{{LEAF}}'>" & [Equities Priced] & "/" & [Equities Tracked] & "</text>"
        & "<text x='28' y='134' font-size='13' font-weight='700' fill='#FFFFFF'>Crypto</text>"
        & "<rect x='130' y='126' width='520' height='9' rx='4.5' fill='rgba(255,255,255,.12)'/><rect x='130' y='126' width='" & FORMAT ( _crw, "0", "en-US" ) & "' height='9' rx='4.5' fill='{{LOSS}}'/>"
        & "<text x='856' y='134' font-size='13' font-weight='700' text-anchor='end' fill='{{LOSS}}'>" & _ok & "/" & _n & "</text>"
        & _chips
        & "<text x='28' y='340' font-size='11' fill='rgba(255,255,255,.55)'>" & ( _n - _ok ) & " crypto pairs have no Alpaca bars · backfill them from Binance once it's enabled</text>"
        & "</svg>"
{SVG_END}"""))

# ───────────────────────── write ─────────────────────────
def slug(s):
    return re.sub(r"[^A-Za-z0-9&+-]+", "-", s.replace("&", "and")).strip("-")

dax_root = os.path.join(ROOT, "dax")
combined = ["// Trading Analytics · all measures", "// Paste into Power BI Desktop → DAX query view → Run → 'Update model with changes'",
            f"// Home table: {HOME}. Display folders follow the dax/ sub-folders.", "DEFINE"]
for folder, name, fmt, expr in M:
    d = os.path.join(dax_root, folder); os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, slug(name) + ".dax"), "w") as fh:
        fh.write(f"-- Measure: {name}\n-- Report: Trading Analytics (The Book · The Edge · The Desk)\n-- Table: {HOME}\n-- Display folder: {folder}\n")
        if fmt: fh.write(f"-- Format string: {fmt}\n")
        fh.write("\n" + expr + "\n")
    body = "\n".join("        " + l for l in expr.splitlines())
    combined.append(f"    MEASURE {HOME}[{name}] =\n{body}")
combined.append("\nEVALUATE\n    ROW ( \"Net P&L\", [Net P&L], \"Trades\", [Trades], \"Win Rate\", [Win Rate] )\n")
open(os.path.join(dax_root, "_all-measures.dax"), "w").write("\n\n".join(combined))
print(len(M), "measures")
