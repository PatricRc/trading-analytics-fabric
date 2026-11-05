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

# ── Design tokens: one source for DAX measures, html/tokens.css and the Power BI theme ──
# Palette (from the Paper design) + an amber accent for markers (PEAK/LOW, PAPER badge)
C = dict(LEAF="#4ED15A", LEAF6="#23803A", LEAF3="#A9E5AE", INK="#0F1712", MUT="#5E685F",
         HAIR="#E3E8E3", LOSS="#C9402F", LOSS3="#F2B5AE", MINT="#E3F5E5", DARK2="#1B2A20",
         AMBER="#F2B33D", CANVAS="#EEF2EE", SURFACE="#FFFFFF")
# semantic names (theme JSON / CSS)
SEM = dict(gain=C["LEAF6"], gain_bright=C["LEAF"], loss=C["LOSS"], loss_soft=C["LOSS3"], neutral=C["MUT"],
           ink=C["INK"], surface=C["SURFACE"], canvas=C["CANVAS"], hairline=C["HAIR"], accent=C["AMBER"], mint=C["MINT"])
SANS = "Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif"
DISPLAY = "Georgia,Cambria,Times New Roman,serif"          # serif display face: page titles, card titles, cover
MONO = "Cascadia Mono,Consolas,Menlo,monospace"           # tickers / strategy ids
TYPE = dict(eyebrow=11, label=12, body=13, sub=14, title=21, h1=40, kpi=44, hero=56)   # px · minimum label 12px on a 1:1 slot
RADIUS = 20                                               # every card, HTML and SVG
SPACE = 8                                                 # 8px grid for padding and gaps inside every card
EYEBROW = f"font-size:{TYPE['eyebrow']}px;font-weight:700;letter-spacing:.09em;text-transform:uppercase"
TAB = "font-variant-numeric:tabular-nums"
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
CARD_CSS = f"font-family:{SANS};border-radius:{RADIUS}px;padding:20px 24px;height:156px;box-sizing:border-box;position:relative;overflow:hidden;{TAB}"
PANEL_CSS = CARD_CSS.replace("height:156px", "height:322px")

def bars(heights_expr):
    """mini bar strip: heights_expr is a DAX list of (value, color) pairs built inline"""
    return heights_expr

def card(name, label, value_expr, sub_expr, dark=False, accent_expr=None, mini=None):
    bg = col("{INK}") if dark else "#FFFFFF"
    fg = "#FFFFFF" if dark else col("{INK}")
    mut = "rgba(255,255,255,.66)" if dark else col("{MUT}")
    edge = "" if dark else f";border:1px solid {C['HAIR']}"
    vcol = accent_expr or f'"{fg}"'
    mini_part = f' & {mini}' if mini else ''
    m(H, name, f"""
VAR _val = {value_expr}
VAR _sub = {sub_expr}
VAR _color = {vcol}
RETURN
    "<div style='{CARD_CSS};background:{bg};color:{fg}{edge}'>"
        & "<div style='{EYEBROW};color:{mut}'>{label}</div>"
        & "<div style='font-size:{TYPE['kpi']}px;font-weight:800;letter-spacing:-.025em;line-height:1;margin-top:18px;color:" & _color & "'>" & _val & "</div>"
        & "<div style='font-size:{TYPE['body']}px;color:{mut};margin-top:12px'>" & _sub & "</div>"{mini_part}
        & "</div>" """)

SIGN = lambda e: f'IF ( {e} < 0, "{C["LOSS"]}", "{C["LEAF6"]}" )'
# signed money with an arrow so colour is never the only signal (WCAG 1.4.1)
UPDN = '"▲$#,0;▼$#,0;$0"'
ARW = lambda e: f'"<span style=\'font-size:22px;vertical-align:8px;margin-right:6px\'>" & IF ( {e} < 0, "▼", "▲" ) & "</span>" & '
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
card("Card - Net Closed P&L HTML", "Net closed P&L", ARW("[Net P&L]") + 'FORMAT ( [Net P&L], "$#,0;$#,0", "en-US" )',
     '"options · equity · crypto (bars)"', accent_expr=SIGN("[Net P&L]"), mini=MINI("[Options P&L]", "[Equity P&L]", "[Crypto P&L]"))
card("Card - Win Rate HTML", "Win rate", 'FORMAT ( [Win Rate], "0.0%", "en-US" )',
     'FORMAT ( [Wins], "#,0" ) & " won · " & FORMAT ( [Losses], "#,0" ) & " lost"', mini=MINI("[Losses]", "[Wins]", "[Wins]"))
card("Card - Profit Factor HTML", "Profit factor", 'FORMAT ( [Profit Factor], "0.00", "en-US" )',
     '"break-even is 1.00 · only crypto clears it (" & FORMAT ( [Crypto Profit Factor], "0.00", "en-US" ) & ")"', mini=MINI("[Gross Losses]", "[Gross Wins]", "[Gross Wins]*[Crypto Profit Factor]/2"))
# Page 2
card("Card - Expectancy HTML", "Expectancy per trade", ARW("[Expectancy]") + 'FORMAT ( [Expectancy], "$#,0.00;$#,0.00", "en-US" )',
     'FORMAT ( [Avg R], "+0.00;-0.00", "en-US" ) & "R" & " avg R-multiple"', dark=True, mini=MINI("[Gross Losses]", "[Gross Wins]", "[Net P&L]"))
card("Card - Lost Past -1R HTML", "Lost past −1R", ARW("[Lost Past -1R P&L]") + 'FORMAT ( [Lost Past -1R P&L] / 1000, "$0.0;$0.0", "en-US" ) & "K"',
     'FORMAT ( [Lost Past -1R Trades], "#,0" ) & " trades slipped their stop"', accent_expr=f'"{C["LOSS"]}"')
card("Card - Won 1R+ HTML", "Won 1R or more", ARW("[Won 1R+ P&L]") + 'FORMAT ( [Won 1R+ P&L] / 1000, "$0.0;$0.0", "en-US" ) & "K"',
     'FORMAT ( [Won 1R+ Trades], "#,0" ) & " trades · the real edge"', accent_expr=f'"{C["LEAF6"]}"')
card("Card - Stop Exits HTML", "Stop exits", 'FORMAT ( [Stop Exits], "#,0" ) & " trades"',
     'FORMAT ( [Stop Exit Recovery %], "0%" ) & " recovered · " & FORMAT ( [Stop Exit P&L], "$#,0;-$#,0", "en-US" )')
# Page 3
card("Card - Capital Deployed HTML", "Capital deployed", 'FORMAT ( [Capital Deployed %], "0%" )',
     '"<b style=\'color:' + C["LEAF"] + '\'>" & FORMAT ( [Position Market Value] / 1000, "$0.0", "en-US" ) & "K" & "</b> of " & FORMAT ( [Account Equity] / 1000, "$0.0", "en-US" ) & "K" & " equity"', dark=True)
card("Card - Unrealized P&L HTML", "Unrealized P&L", ARW("[Unrealized P&L]") + 'FORMAT ( [Unrealized P&L], "$#,0;$#,0", "en-US" )',
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
    f'<span><b style=\'font-size:17px\'>" & {title} & "</b><br><span style=\'font-size:12px;color:{C["MUT"]}\'>" & {sub} & "</span></span></div>"')
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
        & "<div style='display:flex;justify-content:space-between;font-size:12px;color:{C["MUT"]};margin-top:5px'><span>" & _names & "</span><span>Cash " & FORMAT ( [Cash %], "0%" ) & "</span></div>"
        & {ROW('"Buying power " & FORMAT ( [Buying Power], "$#,0", "en-US" )', 'FORMAT ( [Buying Power x Equity], "0.0", "en-US" ) & "× equity · margin unused"', True)}
        & {ROW('[Top Position Symbol] & " is " & FORMAT ( [Top Position Share], "0%" ) & " of exposure"', 'FORMAT ( [Top Position Unrealized], "+$#,0;-$#,0", "en-US" ) & " unrealized"', True)}
        & "</div>" """)
panel("Panel - Shorts vs Longs HTML",
      '"<div style=\'font-size:15px;font-weight:700;margin-bottom:12px\'>" & IF ( [Short P&L] > [Long P&L], "Shorts carry the book", "Longs carry the book" ) & "</div>"'
      ' & "<div style=\'display:flex;gap:10px\'>"'
      f' & "<div style=\'flex:1;background:{C["DARK2"]};border-radius:12px;padding:12px\'><div style=\'font-size:12px;opacity:.6\'>Short · " & [Short Trades] & "</div><div style=\'font-size:26px;font-weight:800;color:{C["LEAF"]}\'>" & FORMAT ( [Short P&L], "+$#,0;-$#,0", "en-US" ) & "</div><div style=\'font-size:12px;opacity:.6\'>" & FORMAT ( [Short Win Rate], "0%" ) & " win</div></div>"'
      f' & "<div style=\'flex:1;background:{C["DARK2"]};border-radius:12px;padding:12px\'><div style=\'font-size:12px;opacity:.6\'>Long · " & [Long Trades] & "</div><div style=\'font-size:26px;font-weight:800;color:{C["LOSS"]}\'>" & FORMAT ( [Long P&L], "+$#,0;-$#,0", "en-US" ) & "</div><div style=\'font-size:12px;opacity:.6\'>" & FORMAT ( [Long Win Rate], "0%" ) & " win</div></div>"'
      ' & "</div>"', dark=True)

# ───────────────────────── 06 · SVG visuals (Image URL / HTML Content) ─────────────────────────
S = "06-svg-visuals"
SVG_END = 'RETURN "data:image/svg+xml;utf8," & SUBSTITUTE ( SUBSTITUTE ( _svg, "%", "%25" ), "#", "%23" )  -- URI-encode % first, then #'
TRADE_DATES = 'FILTER ( ALLSELECTED ( gold_dim_date[Date] ), NOT ISBLANK ( [Net P&L] ) )'

m(S, "SVG - Equity Curve & Drawdown", col(f"""
-- line = cumulative closed P&L; red band underneath = drawdown from the running peak
-- y-axis in $K (12px labels), PEAK / LOW chips and start / end values on the line
VAR _W = 900  VAR _H = 220  VAR _L = 56  VAR _R = 12
VAR _t = ADDCOLUMNS ( {TRADE_DATES}, "@cum", [Cumulative P&L], "@dd", [Drawdown] )
VAR _d0 = MINX ( _t, gold_dim_date[Date] )  VAR _d1 = MAXX ( _t, gold_dim_date[Date] )
VAR _hi = MAX ( 0, MAXX ( _t, [@cum] ) )  VAR _lo = MIN ( 0, MINX ( _t, [@cum] ) )
VAR _ddlo = MIN ( -1, MINX ( _t, [@dd] ) )
VAR _span = MAX ( 1, INT ( _d1 - _d0 ) )
VAR _pts = ADDCOLUMNS ( _t,
    "@x", _L + INT ( gold_dim_date[Date] - _d0 ) / _span * ( _W - _L - _R ),
    "@y", 14 + ( _hi - [@cum] ) / MAX ( 1, _hi - _lo ) * 118,
    "@uy", 156 + [@dd] / _ddlo * 44 )
VAR _line = CONCATENATEX ( _pts, FORMAT ( [@x], "0.0", "en-US" ) & "," & FORMAT ( [@y], "0.0", "en-US" ), " ", gold_dim_date[Date], ASC )
VAR _under = CONCATENATEX ( _pts, FORMAT ( [@x], "0.0", "en-US" ) & "," & FORMAT ( [@uy], "0.0", "en-US" ), " ", gold_dim_date[Date], ASC )
VAR _yv = ( v ) => 0
VAR _y0 = 14 + _hi / MAX ( 1, _hi - _lo ) * 118
VAR _first = TOPN ( 1, _pts, gold_dim_date[Date], ASC )
VAR _last = TOPN ( 1, _pts, gold_dim_date[Date], DESC )
VAR _pk = TOPN ( 1, _pts, [@cum], DESC, gold_dim_date[Date], ASC )
VAR _lw = TOPN ( 1, _pts, [@cum], ASC, gold_dim_date[Date], ASC )
VAR _lx = MAXX ( _last, [@x] )  VAR _ly = MAXX ( _last, [@y] )
VAR _fx = MAXX ( _first, [@x] ) VAR _fy = MAXX ( _first, [@y] )
VAR _px = MAXX ( _pk, [@x] )    VAR _py = MAXX ( _pk, [@y] )   VAR _pv = MAXX ( _pk, [@cum] )
VAR _wx = MAXX ( _lw, [@x] )    VAR _wy = MAXX ( _lw, [@y] )   VAR _wv = MAXX ( _lw, [@cum] )
-- chips stay inside the plot: shift right of the left edge, flip below the point when there is no room above
VAR _pcx = MIN ( MAX ( _px, 106 ), 842 )  VAR _pcy = IF ( _py - 28 < 0, _py + 9, _py - 28 )
VAR _wcx = MIN ( MAX ( _wx, 106 ), 842 )
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 900 220' font-family='{SANS}' >"
        & "<line x1='56' x2='888' y1='14' y2='14' stroke='{{HAIR}}' stroke-dasharray='2 4'/>"
        & "<line x1='56' x2='888' y1='132' y2='132' stroke='{{HAIR}}' stroke-dasharray='2 4'/>"
        & "<line x1='56' x2='888' y1='" & FORMAT ( _y0, "0.0", "en-US" ) & "' y2='" & FORMAT ( _y0, "0.0", "en-US" ) & "' stroke='#BFC8C0'/>"
        & "<text x='48' y='18' font-size='12' text-anchor='end' fill='{{MUT}}'>" & FORMAT ( _hi / 1000, "$0.0K;-$0.0K", "en-US" ) & "</text>"
        & "<text x='48' y='" & FORMAT ( _y0 + 4, "0.0", "en-US" ) & "' font-size='12' text-anchor='end' fill='{{MUT}}'>$0</text>"
        & "<text x='48' y='136' font-size='12' text-anchor='end' fill='{{MUT}}'>" & FORMAT ( _lo / 1000, "$0.0K;-$0.0K", "en-US" ) & "</text>"
        & "<polyline points='" & _line & "' fill='none' stroke='{{LEAF6}}' stroke-width='2.4' stroke-linejoin='round'/>"
        & "<line x1='56' x2='888' y1='156' y2='156' stroke='{{HAIR}}'/>"
        & "<text x='48' y='160' font-size='12' text-anchor='end' fill='{{MUT}}'>DD</text>"
        & "<polygon points='" & FORMAT ( _fx, "0.0", "en-US" ) & ",156 " & _under & " " & FORMAT ( _lx, "0.0", "en-US" ) & ",156' fill='{{LOSS}}' fill-opacity='.18' stroke='{{LOSS}}' stroke-width='1.2'/>"
        & "<circle cx='" & FORMAT ( _fx, "0.0", "en-US" ) & "' cy='" & FORMAT ( _fy, "0.0", "en-US" ) & "' r='3.5' fill='{{INK}}'/>"
        & "<rect x='" & FORMAT ( _pcx - 44, "0.0", "en-US" ) & "' y='" & FORMAT ( _pcy, "0.0", "en-US" ) & "' width='88' height='19' rx='9.5' fill='{{AMBER}}'/>"
        & "<text x='" & FORMAT ( _pcx, "0.0", "en-US" ) & "' y='" & FORMAT ( _pcy + 13.5, "0.0", "en-US" ) & "' font-size='11' font-weight='800' text-anchor='middle' fill='{{INK}}'>PEAK " & FORMAT ( _pv / 1000, "$0.0K;-$0.0K", "en-US" ) & "</text>"
        & "<circle cx='" & FORMAT ( _px, "0.0", "en-US" ) & "' cy='" & FORMAT ( _py, "0.0", "en-US" ) & "' r='4.5' fill='{{AMBER}}' stroke='#fff' stroke-width='1.5'/>"
        & "<rect x='" & FORMAT ( _wcx - 44, "0.0", "en-US" ) & "' y='" & FORMAT ( _wy + 9, "0.0", "en-US" ) & "' width='88' height='19' rx='9.5' fill='{{INK}}'/>"
        & "<text x='" & FORMAT ( _wcx, "0.0", "en-US" ) & "' y='" & FORMAT ( _wy + 22.5, "0.0", "en-US" ) & "' font-size='11' font-weight='800' text-anchor='middle' fill='#fff'>LOW " & FORMAT ( _wv / 1000, "$0.0K;-$0.0K", "en-US" ) & "</text>"
        & "<circle cx='" & FORMAT ( _wx, "0.0", "en-US" ) & "' cy='" & FORMAT ( _wy, "0.0", "en-US" ) & "' r='4.5' fill='{{INK}}' stroke='#fff' stroke-width='1.5'/>"
        & "<circle cx='" & FORMAT ( _lx, "0.0", "en-US" ) & "' cy='" & FORMAT ( _ly, "0.0", "en-US" ) & "' r='5' fill='{{LEAF6}}' stroke='#fff' stroke-width='1.5'/>"
        & "<text x='" & FORMAT ( _lx - 10, "0.0", "en-US" ) & "' y='" & FORMAT ( _ly - 12, "0.0", "en-US" ) & "' font-size='13' font-weight='800' text-anchor='end' fill='{{INK}}'>Now " & FORMAT ( [Net P&L], "$#,0;-$#,0", "en-US" ) & "</text>"
        & "<text x='" & FORMAT ( _fx, "0.0", "en-US" ) & "' y='216' font-size='12' fill='{{MUT}}'>" & FORMAT ( _d0, "d mmm", "en-US" ) & "</text>"
        & "<text x='888' y='216' font-size='12' text-anchor='end' fill='{{MUT}}'>" & FORMAT ( _d1, "d mmm", "en-US" ) & "</text>"
        & "<text x='470' y='216' font-size='12' font-weight='700' text-anchor='middle' fill='{{LOSS}}'>Max drawdown " & FORMAT ( _ddlo, "$#,0;-$#,0", "en-US" ) & "</text>"
        & "</svg>"
{SVG_END}""").replace("VAR _yv = ( v ) => 0\n", "").replace("VAR _k = ( v ) => 0\n", ""))

m(S, "SVG - P&L Waterfall", col(f"""
-- gross wins → stop exits → other losses → net (bars start from zero, per the style guide)
VAR _gw = [Gross Wins]  VAR _st = [Stop Exit P&L]  VAR _ot = [Other Losses]  VAR _net = [Net P&L]
VAR _min = MIN ( 0, _net )  VAR _max = _gw
VAR _X = ( v ) => 0   -- placeholder, Power BI does not support lambdas; see inline math below
VAR _sc = 600 / ( _max - _min )
VAR _z = 150 - _min * _sc
VAR _x1 = _z + _gw * _sc  VAR _x2 = _x1 + _st * _sc  VAR _x3 = _x2 + _ot * _sc
VAR _row = ( 0 )
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 900 150' font-family='Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif' font-size='14'>"
        & "<line x1='" & FORMAT ( _z, "0.0", "en-US" ) & "' x2='" & FORMAT ( _z, "0.0", "en-US" ) & "' y1='0' y2='136' stroke='#BFC8C0'/>"
        & "<text x='0' y='19' fill='{{INK}}'>Gross wins</text><rect x='" & FORMAT ( _z, "0.0", "en-US" ) & "' y='4' width='" & FORMAT ( ( _x1 - _z ), "0.0", "en-US" ) & "' height='22' rx='6' fill='{{LEAF6}}'/>"
        & "<text x='896' y='19' text-anchor='end' font-weight='700' fill='{{LEAF6}}'>" & FORMAT ( _gw, "+$#,0", "en-US" ) & "</text>"
        & "<text x='0' y='53' fill='{{INK}}'>Stop exits</text><rect x='" & FORMAT ( _x2, "0.0", "en-US" ) & "' y='38' width='" & FORMAT ( ( _x1 - _x2 ), "0.0", "en-US" ) & "' height='22' rx='6' fill='{{LOSS}}'/>"
        & "<text x='896' y='53' text-anchor='end' font-weight='700' fill='{{LOSS}}'>" & FORMAT ( _st, "$#,0;-$#,0", "en-US" ) & "</text>"
        & "<text x='0' y='87' fill='{{INK}}'>Other losses</text><rect x='" & FORMAT ( _x3, "0.0", "en-US" ) & "' y='72' width='" & FORMAT ( ( _x2 - _x3 ), "0.0", "en-US" ) & "' height='22' rx='6' fill='{{LOSS3}}'/>"
        & "<text x='896' y='87' text-anchor='end' font-weight='700' fill='{{LOSS}}'>" & FORMAT ( _ot, "$#,0;-$#,0", "en-US" ) & "</text>"
        & "<text x='0' y='121' font-weight='700' fill='{{INK}}'>Net P&amp;L</text><rect x='" & FORMAT ( MIN ( _z, _x3 ), "0.0", "en-US" ) & "' y='106' width='" & FORMAT ( ABS ( _z - _x3 ), "0.0", "en-US" ) & "' height='22' rx='6' fill='{{INK}}'/>"
        & "<text x='896' y='121' text-anchor='end' font-weight='700' fill='{{INK}}'>" & FORMAT ( _net, "$#,0;-$#,0", "en-US" ) & "</text>"
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
-- 4 best and 4 worst strategies · columns: name | trades | stem from $0 + value | win-rate chip
VAR _all = ADDCOLUMNS ( ALLSELECTED ( gold_fact_trades[strategy] ), "@v", [Net P&L], "@n", [Trades], "@w", [Win Rate] )
VAR _sel = UNION ( TOPN ( 4, _all, [@v], DESC ), TOPN ( 4, _all, [@v], ASC ) )
VAR _rk = ADDCOLUMNS ( _sel, "@i", RANKX ( _sel, [@v], , DESC, DENSE ) )
VAR _m = MAX ( MAXX ( _sel, ABS ( [@v] ) ), 1 )
VAR _maxn = MAXX ( _sel, [@n] )
VAR _z = 590
VAR _rows = CONCATENATEX ( _rk,
    VAR y = FORMAT ( 30 + ( [@i] - 1 ) * 24.5, "0.0", "en-US" )
    VAR yt = FORMAT ( 34.5 + ( [@i] - 1 ) * 24.5, "0.0", "en-US" )
    VAR x = _z + [@v] / _m * 180
    VAR c = IF ( [@v] >= 0, "{{LEAF6}}", "{{LOSS}}" )
    VAR wc = IF ( [@w] >= 0.5, "{{LEAF6}}", "{{LOSS}}" )
    RETURN
        "<text x='0' y='" & yt & "' font-family='{MONO}' font-size='13' fill='{{INK}}'>" & gold_fact_trades[strategy] & "</text>"
        & "<text x='300' y='" & yt & "' font-size='12' text-anchor='end' fill='{{MUT}}'>" & [@n] & "</text>"
        & "<line x1='" & FORMAT ( _z, "0.0", "en-US" ) & "' x2='" & FORMAT ( x, "0.0", "en-US" ) & "' y1='" & y & "' y2='" & y & "' stroke='" & c & "' stroke-width='2'/>"
        & "<circle cx='" & FORMAT ( x, "0.0", "en-US" ) & "' cy='" & y & "' r='" & FORMAT ( 4 + 5 * SQRT ( [@n] / _maxn ), "0.0", "en-US" ) & "' fill='" & c & "' stroke='#fff' stroke-width='1.5'/>"
        & "<text x='" & FORMAT ( x + IF ( [@v] >= 0, 14, -14 ), "0.0", "en-US" ) & "' y='" & yt & "' font-size='13' font-weight='800' fill='" & c & "' text-anchor='" & IF ( [@v] >= 0, "start", "end" ) & "'>" & FORMAT ( [@v], "+$#,0;-$#,0", "en-US" ) & "</text>"
        & "<rect x='846' y='" & FORMAT ( 30 + ( [@i] - 1 ) * 24.5 - 9, "0.0", "en-US" ) & "' width='50' height='18' rx='9' fill='" & wc & "' fill-opacity='.12'/>"
        & "<text x='871' y='" & yt & "' font-size='12' font-weight='700' text-anchor='middle' fill='" & wc & "'>" & FORMAT ( [@w], "0%" ) & "</text>",
    "", [@i], ASC )
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 900 228' font-family='{SANS}'>"
        & "<text x='0' y='10' font-size='11' font-weight='700' letter-spacing='1' fill='{{MUT}}'>STRATEGY</text>"
        & "<text x='300' y='10' font-size='11' font-weight='700' letter-spacing='1' text-anchor='end' fill='{{MUT}}'>TRADES</text>"
        & "<text x='590' y='10' font-size='11' font-weight='700' letter-spacing='1' text-anchor='middle' fill='{{MUT}}'>NET P&amp;L</text>"
        & "<text x='871' y='10' font-size='11' font-weight='700' letter-spacing='1' text-anchor='middle' fill='{{MUT}}'>WIN</text>"
        & "<line x1='" & FORMAT ( _z, "0.0", "en-US" ) & "' x2='" & FORMAT ( _z, "0.0", "en-US" ) & "' y1='18' y2='222' stroke='#BFC8C0'/>"
        & "<line x1='0' x2='900' y1='121.5' y2='121.5' stroke='{{HAIR}}' stroke-dasharray='2 4'/>" & _rows & "</svg>"
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
        & "<text x='" & cx & "' y='" & ( 168 - INT ( MAX ( n - 1, 0 ) / 4 ) * 10 - 10 ) & "' font-size='12' font-weight='700' text-anchor='middle' fill='{{INK}}'>" & n & "</text>"
        & "<text x='" & cx & "' y='202' font-size='12' text-anchor='middle' fill='{{MUT}}'>" & FORMAT ( b, "+0.0;-0.0;0", "en-US" ) & "R" & "</text>",
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
        & "<text x='140' y='126' font-size='12' text-anchor='end' fill='{{MUT}}'>orders</text>"
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
        & "<text x='50' y='66' font-size='9' font-weight='700' text-anchor='middle' fill='{{MUT}}'>INVESTED</text></svg>"
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
    edge = "" if dark else f" stroke='{C['HAIR']}'"
    ix, iy, iw, ih = inner_box
    iw = iw or w - 2 * ix
    ih = ih or h - iy - 20
    m(L1, name, f"""
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' font-family='Plus Jakarta Sans,Segoe UI,sans-serif'>"
        & "<rect width='{w}' height='{h}' rx='20' fill='{bg}'{edge}/>"
        & "<text x='28' y='44' font-family='{DISPLAY}' font-size='23' font-weight='700' fill='{tc}'>" & {title_expr} & "</text>"
        & "<text x='28' y='68' font-size='13' fill='{mc}'>" & {sub_expr} & "</text>"
        & {extra}
        & "<svg x='{ix}' y='{iy}' width='{iw}' height='{ih}'>" & {RAW(inner)} & "</svg>"
        & "</svg>"
{SVG_END}""")

def pill(x, y, w, text_expr, bg, fg, h=26):
    return (f'"<rect x=\'{x}\' y=\'{y}\' width=\'{w}\' height=\'{h}\' rx=\'{h//2}\' fill=\'{bg}\'/>'
            f'<text x=\'{x + w/2}\' y=\'{y + h/2 + 4}\' font-size=\'12\' font-weight=\'700\' text-anchor=\'middle\' fill=\'{fg}\'>" & {text_expr} & "</text>"')

framed("SVG - Card Equity Curve", "SVG - Equity Curve & Drawdown", 884, 340,
       '"Equity curve &amp; drawdown"', '"Cumulative closed P&amp;L by day · shaded = distance below the running peak"',
       extra=pill(736, 22, 120, '"Daily · closed"', C["MINT"], C["LEAF6"]))
framed("SVG - Card Waterfall", "SVG - P&L Waterfall", 884, 358,
       "[Title - The Book]", '"P&amp;L waterfall · stop exits alone erase more than half of all gains"',
       extra=pill(686, 22, 170, '"Stops = " & FORMAT ( [Stop Share of Gains], "0%" ) & " of gains"', "#FDE7E4", C["LOSS"]),
       inner_box=(28, 100, None, 230))
m(L1, "SVG - Card Crypto", col(f"""
-- dark card: weekly cumulative lines + one bar per asset class
VAR _c = [Crypto P&L]  VAR _e = [Equity P&L]  VAR _o = [Options P&L]
VAR _mx = MAX ( ABS ( _c ), MAX ( ABS ( _e ), ABS ( _o ) ) )
VAR _bar = 560
VAR _row = ( 0 )
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 884 358' font-family='Plus Jakarta Sans,Segoe UI,sans-serif'>"
        & "<rect width='884' height='358' rx='20' fill='{{INK}}'/>"
        & "<text x='28' y='44' font-family='{DISPLAY}' font-size='23' font-weight='700' fill='#FFFFFF'>" & IF ( _c > MAX ( _e, _o ), "Only crypto pays", "Crypto is not the winner" ) & "</text>"
        & "<text x='28' y='68' font-size='13' fill='rgba(255,255,255,.6)'>Cumulative P&amp;L by week</text>"
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


def header_measure(folder, name, title, sub_expr, chip_expr):
    """page header: serif title, question subtitle, two static chips (no fake dropdowns)"""
    m(folder, name, f"""
VAR _chip = {chip_expr}
VAR _cw = 28 + LEN ( _chip ) * 8.2
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1792 96' font-family='{SANS}'>"
        & "<text x='0' y='48' font-family='{DISPLAY}' font-size='42' font-weight='700' letter-spacing='-.5' fill='{C['INK']}'>{title}</text>"
        & "<text x='2' y='80' font-size='15' fill='{C['MUT']}'>" & {sub_expr} & "</text>"
        & "<rect x='" & FORMAT ( 1792 - _cw - 186, "0", "en-US" ) & "' y='26' width='174' height='42' rx='21' fill='#FFFFFF' stroke='{C['HAIR']}'/>"
        & "<circle cx='" & FORMAT ( 1792 - _cw - 164, "0", "en-US" ) & "' cy='47' r='5' fill='{C['AMBER']}'/>"
        & "<text x='" & FORMAT ( 1792 - _cw - 150, "0", "en-US" ) & "' y='52' font-size='14' font-weight='700' fill='{C['INK']}'>Alpaca · Paper</text>"
        & "<rect x='" & FORMAT ( 1792 - _cw, "0", "en-US" ) & "' y='26' width='" & FORMAT ( _cw, "0", "en-US" ) & "' height='42' rx='21' fill='{C['INK']}'/>"
        & "<text x='" & FORMAT ( 1792 - _cw / 2, "0", "en-US" ) & "' y='52' font-size='14' font-weight='700' text-anchor='middle' fill='#FFFFFF'>" & _chip & "</text>"
        & "</svg>"
{SVG_END}""")

RANGE = 'FORMAT ( [First Trade Date], "d mmm", "en-US" ) & " – " & FORMAT ( [Last Trade Date], "d mmm yyyy", "en-US" )'

header_measure(L1, "SVG - Header The Book", "The Book", "[Subtitle - The Book]", RANGE)

def rail_measure(folder, name, active):
    items = [("Home", "<path d='M26 {c} L36 {c2} L46 {c} V{c3} H26 Z' fill='none' stroke='{s}' stroke-width='2' stroke-linejoin='round'/>"),
             ("Book", "<polyline points='26,{a} 32,{b} 38,{d} 46,{e}' fill='none' stroke='{s}' stroke-width='2' stroke-linecap='round'/><line x1='26' y1='{f}' x2='46' y2='{f}' stroke='{s}' stroke-width='2'/>"),
             ("Edge", "<circle cx='36' cy='{c}' r='10' fill='none' stroke='{s}' stroke-width='2'/><circle cx='36' cy='{c}' r='3.5' fill='{s}'/>"),
             ("Desk", "<rect x='26' y='{a}' width='20' height='16' rx='3' fill='none' stroke='{s}' stroke-width='2'/><line x1='26' y1='{b}' x2='46' y2='{b}' stroke='{s}' stroke-width='2'/>"),
             ("Ledger", "<line x1='26' y1='{a}' x2='46' y2='{a}' stroke='{s}' stroke-width='2'/><line x1='26' y1='{c}' x2='46' y2='{c}' stroke='{s}' stroke-width='2'/><line x1='26' y1='{b}' x2='40' y2='{b}' stroke='{s}' stroke-width='2'/>")]
    parts = []
    for i, (label, icon) in enumerate(items):
        top = 96 + i * 76; c = top + 30
        on = i == active
        st = C["INK"] if on else "rgba(255,255,255,.55)"
        if on:
            parts.append(f"<rect x='8' y='{top + 6}' width='56' height='64' rx='14' fill='{C['LEAF']}'/>")
        parts.append(icon.format(c=c, c2=c - 10, c3=c + 9, a=c - 6, b=c + 6, d=c - 2, e=c - 10, f=c + 8, s=st))
        parts.append(f"<text x='36' y='{top + 60}' font-size='11' font-weight='{800 if on else 600}' text-anchor='middle' fill='{st if on else 'rgba(255,255,255,.62)'}'>{label}</text>")
    body = "".join(parts)
    m(folder, name, f"""
-- left navigation rail · active item = {items[active][0]} (green pill); a transparent vertical
-- Page navigator (x 0, y 96, 72 x 380, 5 buttons of 76px) sits on top and does the actual navigation
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 72 1080' font-family='{SANS}'>"
        & "<rect width='72' height='1080' fill='{C['INK']}'/>"
        & "<rect x='14' y='24' width='44' height='44' rx='12' fill='{C['LEAF']}'/>"
        & "<polyline points='24,54 32,44 40,50 49,38' fill='none' stroke='{C['INK']}' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'/>"
        & "{body}"
        & "<circle cx='36' cy='1026' r='5' fill='{C['AMBER']}'/>"
        & "<text x='36' y='1052' font-size='10' font-weight='800' letter-spacing='1.5' text-anchor='middle' fill='{C['AMBER']}'>PAPER</text>"
        & "</svg>"
{SVG_END}""")

rail_measure(L1, "SVG - Rail", 1)

# ───────────────────────── 08 · page 2 layout (The Edge) ─────────────────────────
L2 = "08-page2-layout"
rail_measure(L2, "SVG - Rail The Edge", 2)
rail_measure("09-page3-layout", "SVG - Rail The Desk", 3)

header_measure(L2, "SVG - Header The Edge", "The Edge",
    '"Where do the wins and losses come from? · R-multiples · exits · " & FORMAT ( [Strategies], "0" ) & " strategies"', RANGE)

def framed2(name, inner, w, h, title_expr, sub_expr, extra='""', inner_box=(28, 88, None, None)):
    ix, iy, iw, ih = inner_box
    iw = iw or w - 2 * ix
    ih = ih or h - iy - 20
    m(L2, name, f"""
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {w} {h}' font-family='Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif'>"
        & "<rect width='{w}' height='{h}' rx='20' fill='#FFFFFF' stroke='{{HAIR}}'/>"
        & "<text x='28' y='44' font-family='{DISPLAY}' font-size='23' font-weight='700' fill='{C["INK"]}'>" & {title_expr} & "</text>"
        & "<text x='28' y='68' font-size='13' fill='{C["MUT"]}'>" & {sub_expr} & "</text>"
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
        extra=pill(686, 22, 170, 'FORMAT ( [Lost Past -1R Trades], "0" ) & " slipped the stop"', "#FDE7E4", C["LOSS"]),
        inner_box=(28, 92, None, 246))

m(L2, "SVG - Card Shorts vs Longs", col(f"""
-- dark card: short vs long scorecards + one tick per trade
VAR _sp = [Short P&L]  VAR _lp = [Long P&L]
VAR _box = ( 0 )
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 884 358' font-family='Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif'>"
        & "<rect width='884' height='358' rx='20' fill='{{INK}}'/>"
        & "<text x='28' y='44' font-family='{DISPLAY}' font-size='23' font-weight='700' fill='#FFFFFF'>" & IF ( _sp > _lp, "Shorts carry the book", "Longs carry the book" ) & "</text>"
        & "<text x='28' y='68' font-size='13' fill='rgba(255,255,255,.6)'>Net P&amp;L and win rate by side</text>"
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
header_measure(L3, "SVG - Header The Desk", "The Desk",
    '"What is open right now? · positions · cash · order flow"',
    '"As of " & FORMAT ( CALCULATE ( MAX ( gold_fact_account[Date] ), REMOVEFILTERS ( gold_dim_date ) ), "d mmm yyyy", "en-US" )')

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
        "<rect x='" & FORMAT ( [@x0] + 2, "0.0", "en-US" ) & "' y='96' width='" & FORMAT ( MAX ( w - 4, 1 ), "0.0", "en-US" ) & "' height='212' rx='10' fill='" & c & "'/>"
        & IF ( w >= 9 * LEN ( gold_fact_positions[symbol] ) + 24,
            "<text x='" & FORMAT ( [@x0] + 12, "0.0", "en-US" ) & "' y='120' font-size='14' font-weight='800' fill='" & tc & "'>" & gold_fact_positions[symbol] & "</text>"
            & "<text x='" & FORMAT ( [@x0] + 12, "0.0", "en-US" ) & "' y='137' font-size='12' fill='" & tc & "' fill-opacity='.85'>" & FORMAT ( [@mv], "$#,0", "en-US" ) & " · " & FORMAT ( DIVIDE ( [@mv], _tot ), "0%" ) & "</text>"
            & "<text x='" & FORMAT ( [@x0] + w - 10, "0.0", "en-US" ) & "' y='296' font-size='14' font-weight='800' text-anchor='end' fill='" & tc & "'>" & FORMAT ( [@r], "+0.00%;-0.00%", "en-US" ) & "</text>" ),
    "", [@i], ASC )
VAR _small = COUNTROWS ( FILTER ( _x, [@mv] / _tot * 828 < 9 * LEN ( gold_fact_positions[symbol] ) + 24 ) )
VAR _smallList = CONCATENATEX ( FILTER ( _x, [@mv] / _tot * 828 < 9 * LEN ( gold_fact_positions[symbol] ) + 24 ), gold_fact_positions[symbol] & " " & FORMAT ( [@r], "+0.0%;-0.0%", "en-US" ), " · ", [@i], ASC )
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 884 340' font-family='Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif'>"
        & "<rect width='884' height='340' rx='20' fill='#FFFFFF' stroke='{{HAIR}}'/>"
        & "<text x='28' y='44' font-family='{DISPLAY}' font-size='23' font-weight='700' fill='{{INK}}'>Open positions · " & IF ( [Top Position Share] >= 0.3, "one name carries the gain", "exposure is spread out" ) & "</text>"
        & "<text x='28' y='68' font-size='13' fill='{{MUT}}'>Tile area = market value · colour = return on cost · " & FORMAT ( [Open Positions], "0" ) & " open positions</text>"
        & "<rect x='700' y='30' width='14' height='10' rx='2' fill='{{LOSS}}'/><rect x='716' y='30' width='14' height='10' rx='2' fill='{{LOSS3}}'/>"
        & "<rect x='732' y='30' width='14' height='10' rx='2' fill='{{LEAF3}}'/><rect x='748' y='30' width='14' height='10' rx='2' fill='{{LEAF6}}'/>"
        & "<text x='770' y='39' font-size='11' fill='{{MUT}}'>−1% → +1%</text>"
        & _tiles
        & IF ( _small > 0, "<text x='28' y='328' font-size='12' fill='{{MUT}}'>+" & _small & " smaller: " & _smallList & "</text>" )
        & "</svg>"
{SVG_END}"""))

m(L3, "SVG - Card Order Flow", col(f"""
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 884 358' font-family='Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif'>"
        & "<rect width='884' height='358' rx='20' fill='#FFFFFF' stroke='{{HAIR}}'/>"
        & "<text x='28' y='44' font-family='{DISPLAY}' font-size='23' font-weight='700' fill='{{INK}}'>Where " & FORMAT ( [Orders], "#,0", "en-US" ) & " orders went</text>"
        & "<text x='28' y='68' font-size='13' fill='{{MUT}}'>Order flow: all orders → side → outcome · band width = order count</text>"
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
        & "<text x='" & ( cx + 31 ) & "' y='" & ( cy + 15 ) & "' font-size='12' font-weight='700' text-anchor='middle' fill='" & c & "'>" & LEFT ( gold_dim_symbol[base], 7 ) & "</text>",
    "", [@i], ASC )
VAR _eqw = 520 * DIVIDE ( [Equities Priced], [Equities Tracked] )
VAR _crw = 520 * DIVIDE ( _ok, _n )
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 884 358' font-family='Plus Jakarta Sans,Segoe UI,Helvetica,Arial,sans-serif'>"
        & "<rect width='884' height='358' rx='20' fill='{{INK}}'/>"
        & "<text x='28' y='44' font-family='{DISPLAY}' font-size='23' font-weight='700' fill='#FFFFFF'>Market coverage</text>"
        & "<text x='28' y='68' font-size='13' fill='rgba(255,255,255,.6)'>Symbols with daily price bars on Alpaca</text>"
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


# ───────────────────────── 10 · cover + ledger pages ─────────────────────────
L4 = "10-cover-and-ledger"
m(L4, "SVG - Cover", col(f"""
-- page 0 (1920 x 1080): title, three headline numbers, how-to-read strip and a hero drawn from the
-- real daily equity path (one candle per trading day: open = previous cumulative P&L, close = today's)
VAR _t = ADDCOLUMNS ( {TRADE_DATES}, "@cum", [Cumulative P&L], "@day", [Net P&L] )
VAR _n = COUNTROWS ( _t )
VAR _hi = MAXX ( _t, MAX ( [@cum], [@cum] - [@day] ) )  VAR _lo = MINX ( _t, MIN ( [@cum], [@cum] - [@day] ) )
VAR _r = ADDCOLUMNS ( _t, "@i", RANKX ( _t, gold_dim_date[Date], , ASC ) )
VAR _cw = 860 / _n
VAR _candles = CONCATENATEX ( _r,
    VAR x = 1000 + ( [@i] - 1 ) * _cw
    VAR o = 200 + ( _hi - ( [@cum] - [@day] ) ) / ( _hi - _lo ) * 420
    VAR c = 200 + ( _hi - [@cum] ) / ( _hi - _lo ) * 420
    VAR k = IF ( [@day] >= 0, "{{LEAF}}", "{{LOSS}}" )
    RETURN "<line x1='" & FORMAT ( x + _cw / 2, "0.0", "en-US" ) & "' x2='" & FORMAT ( x + _cw / 2, "0.0", "en-US" ) & "' y1='" & FORMAT ( MIN ( o, c ) - 8, "0.0", "en-US" ) & "' y2='" & FORMAT ( MAX ( o, c ) + 8, "0.0", "en-US" ) & "' stroke='" & k & "' stroke-opacity='.45'/>"
        & "<rect x='" & FORMAT ( x + 2, "0.0", "en-US" ) & "' y='" & FORMAT ( MIN ( o, c ), "0.0", "en-US" ) & "' width='" & FORMAT ( MAX ( _cw - 4, 2 ), "0.0", "en-US" ) & "' height='" & FORMAT ( MAX ( ABS ( c - o ), 2 ), "0.0", "en-US" ) & "' rx='2' fill='" & k & "' fill-opacity='.8'/>",
    "", [@i], ASC )
VAR _z = 200 + _hi / ( _hi - _lo ) * 420
VAR _svg =
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1920 1080' font-family='{SANS}'>"
        & "<defs><radialGradient id='g' cx='75%' cy='35%' r='70%'><stop offset='0' stop-color='{{DARK2}}'/><stop offset='1' stop-color='{{INK}}'/></radialGradient>"
        & "<pattern id='p' width='24' height='24' patternUnits='userSpaceOnUse'><path d='M24 0 H0 V24' fill='none' stroke='#fff' stroke-opacity='.035'/></pattern></defs>"
        & "<rect width='1920' height='1080' fill='url(#g)'/><rect width='1920' height='1080' fill='url(#p)'/>"
        & "<line x1='1000' x2='1860' y1='" & FORMAT ( _z, "0.0", "en-US" ) & "' y2='" & FORMAT ( _z, "0.0", "en-US" ) & "' stroke='#fff' stroke-opacity='.25' stroke-dasharray='3 6'/>"
        & "<text x='1860' y='" & FORMAT ( _z - 10, "0.0", "en-US" ) & "' font-size='14' text-anchor='end' fill='#fff' fill-opacity='.5'>$0 · start of book</text>"
        & _candles
        & "<text x='1000' y='680' font-size='14' fill='#fff' fill-opacity='.5'>One candle per trading day · cumulative closed P&amp;L · " & FORMAT ( _n, "0" ) & " days</text>"
        & "<rect x='120' y='96' width='52' height='52' rx='14' fill='{{LEAF}}'/>"
        & "<polyline points='132,132 142,120 151,127 162,113' fill='none' stroke='{{INK}}' stroke-width='3.5' stroke-linecap='round' stroke-linejoin='round'/>"
        & "<text x='188' y='131' font-size='22' font-weight='800' fill='#fff'>DataPat<tspan fill='{{LEAF}}'>.ai</tspan></text>"
        & "<text x='120' y='300' font-size='15' font-weight='800' letter-spacing='3' fill='{{AMBER}}'>ALPACA · PAPER ACCOUNT · " & UPPER ( FORMAT ( [First Trade Date], "d mmm", "en-US" ) & " – " & FORMAT ( [Last Trade Date], "d mmm yyyy", "en-US" ) ) & "</text>"
        & "<text x='116' y='392' font-family='{DISPLAY}' font-size='88' font-weight='700' fill='#fff'>The Book of a</text>"
        & "<text x='116' y='488' font-family='{DISPLAY}' font-size='88' font-weight='700' font-style='italic' fill='{{LEAF}}'>Paper Trader</text>"
        & "<text x='120' y='548' font-size='22' fill='#fff' fill-opacity='.72'>" & FORMAT ( [Trades], "#,0" ) & " closed trades, " & FORMAT ( [Strategies], "0" ) & " strategies and one honest question: is there an edge?</text>"
        & "<g fill='#fff'>"
        & "<text x='120' y='628' font-size='13' font-weight='800' letter-spacing='2' fill-opacity='.55'>ACCOUNT EQUITY</text>"
        & "<text x='120' y='692' font-size='60' font-weight='800' letter-spacing='-1'>" & FORMAT ( [Account Equity], "$#,0", "en-US" ) & "</text>"
        & "<text x='420' y='628' font-size='13' font-weight='800' letter-spacing='2' fill-opacity='.55'>NET CLOSED P&amp;L</text>"
        & "<text x='420' y='692' font-size='60' font-weight='800' letter-spacing='-1' fill='" & IF ( [Net P&L] < 0, "#FF7A6E", "{{LEAF}}" ) & "'>" & FORMAT ( [Net P&L], "+$#,0;-$#,0", "en-US" ) & "</text>"
        & "<text x='700' y='628' font-size='13' font-weight='800' letter-spacing='2' fill-opacity='.55'>PROFIT FACTOR</text>"
        & "<text x='700' y='692' font-size='60' font-weight='800' letter-spacing='-1'>" & FORMAT ( [Profit Factor], "0.00", "en-US" ) & "</text></g>"
        & "<rect x='120' y='744' width='300' height='64' rx='32' fill='{{LEAF}}'/>"
        & "<text x='270' y='784' font-size='20' font-weight='800' text-anchor='middle' fill='{{INK}}'>Explore the book  →</text>"
        & "<rect x='440' y='744' width='170' height='64' rx='32' fill='none' stroke='#fff' stroke-opacity='.4'/>"
        & "<text x='525' y='784' font-size='18' font-weight='700' text-anchor='middle' fill='#fff'>LinkedIn ↗</text>"
        & "<rect x='626' y='744' width='170' height='64' rx='32' fill='none' stroke='#fff' stroke-opacity='.4'/>"
        & "<text x='711' y='784' font-size='18' font-weight='700' text-anchor='middle' fill='#fff'>Portfolio ↗</text>"
        & "<line x1='120' x2='1800' y1='880' y2='880' stroke='#fff' stroke-opacity='.15'/>"
        & "<text x='120' y='920' font-size='13' font-weight='800' letter-spacing='2' fill='{{AMBER}}'>HOW TO READ</text>"
        & "<text x='120' y='962' font-size='18' font-weight='800' fill='#fff'>R-multiple</text>"
        & "<text x='120' y='992' font-size='16' fill='#fff' fill-opacity='.68'>Net P&amp;L ÷ planned risk. +1R = won what you risked;</text>"
        & "<text x='120' y='1016' font-size='16' fill='#fff' fill-opacity='.68'>past −1R = the stop slipped.</text>"
        & "<text x='700' y='962' font-size='18' font-weight='800' fill='#fff'>Profit factor</text>"
        & "<text x='700' y='992' font-size='16' fill='#fff' fill-opacity='.68'>Gross wins ÷ gross losses. Above 1.00 makes money,</text>"
        & "<text x='700' y='1016' font-size='16' fill='#fff' fill-opacity='.68'>below 1.00 loses it.</text>"
        & "<text x='1280' y='962' font-size='18' font-weight='800' fill='{{AMBER}}'>Why “PAPER” matters</text>"
        & "<text x='1280' y='992' font-size='16' fill='#fff' fill-opacity='.68'>Simulated fills on Alpaca’s paper account: no real</text>"
        & "<text x='1280' y='1016' font-size='16' fill='#fff' fill-opacity='.68'>capital, no slippage cost. Treat results as a rehearsal.</text>"
        & "<text x='1800' y='131' font-size='15' text-anchor='end' fill='#fff' fill-opacity='.6'>Patricio Rios · Microsoft Fabric + Power BI</text>"
        & "</svg>"
{SVG_END}"""))

rail_measure(L4, "SVG - Rail The Ledger", 4)
header_measure(L4, "SVG - Header The Ledger", "The Ledger",
    '"Every strategy, grouped by asset class · sorted by net P&amp;L · status = Edge / Watch / Cut"', RANGE)

m(L4, "Strategy Status", """
-- Edge = profit factor >= 1.2 on 10+ trades · Cut = losing more than $500 with PF < 0.8 · otherwise Watch
SWITCH ( TRUE (),
    [Profit Factor] >= 1.2 && [Trades] >= 10, "Edge",
    [Net P&L] < -500 && [Profit Factor] < 0.8, "Cut",
    "Watch" )""")

LEDGER_TD = "padding:7px 12px;border-bottom:1px solid " + C["HAIR"]
m(L4, "HTML - Ledger", col(f"""
-- explore page: one row per strategy inside its asset class, heat bar on net P&L, status pill
VAR _maxAbs = MAXX ( ALLSELECTED ( gold_fact_trades[strategy] ), ABS ( [Net P&L] ) )
VAR _th = "<th style='{EYEBROW};color:{{MUT}};text-align:right;padding:10px 12px;border-bottom:2px solid {{INK}}'>"
VAR _classes = ADDCOLUMNS ( VALUES ( gold_fact_trades[asset_class] ), "@v", [Net P&L] )
VAR _body = CONCATENATEX ( _classes,
    VAR _cls = gold_fact_trades[asset_class]
    VAR _nice = SWITCH ( _cls, "crypto", "Crypto", "us_equity", "Equity", "us_option", "Options", _cls )
    VAR _rows = ADDCOLUMNS ( CALCULATETABLE ( VALUES ( gold_fact_trades[strategy] ), gold_fact_trades[asset_class] = _cls ),
        "@v", CALCULATE ( [Net P&L], gold_fact_trades[asset_class] = _cls ),
        "@n", CALCULATE ( [Trades], gold_fact_trades[asset_class] = _cls ),
        "@w", CALCULATE ( [Win Rate], gold_fact_trades[asset_class] = _cls ),
        "@r", CALCULATE ( [Avg R], gold_fact_trades[asset_class] = _cls ),
        "@pf", CALCULATE ( [Profit Factor], gold_fact_trades[asset_class] = _cls ),
        "@s", CALCULATE ( [Strategy Status], gold_fact_trades[asset_class] = _cls ) )
    RETURN
        "<tr style='background:{{CANVAS}}'><td colspan='7' style='padding:12px;font-family:{DISPLAY};font-size:19px;font-weight:700'>" & _nice
            & "<span style='font-family:{SANS};font-size:13px;font-weight:600;color:{{MUT}};margin-left:12px'>" & FORMAT ( CALCULATE ( [Trades] ), "#,0" ) & " trades · "
            & "<b style='color:" & IF ( [@v] < 0, "{{LOSS}}", "{{LEAF6}}" ) & "'>" & IF ( [@v] < 0, "▼ ", "▲ " ) & FORMAT ( [@v], "+$#,0;-$#,0", "en-US" ) & "</b></span></td></tr>"
        & CONCATENATEX ( _rows,
            VAR _c = IF ( [@v] < 0, "{{LOSS}}", "{{LEAF6}}" )
            VAR _pill = SWITCH ( [@s], "Edge", "background:{{MINT}};color:{{LEAF6}}", "Cut", "background:#FBE3E0;color:{{LOSS}}", "background:#FFF3DA;color:#8A5A00" )
            RETURN "<tr>"
                & "<td style='{LEDGER_TD};font-family:{MONO};font-size:14px'>" & gold_fact_trades[strategy] & "</td>"
                & "<td style='{LEDGER_TD};text-align:right'>" & FORMAT ( [@n], "#,0" ) & "</td>"
                & "<td style='{LEDGER_TD};text-align:right;white-space:nowrap'><span style='display:inline-block;vertical-align:middle;width:140px;height:10px;margin-right:12px;background:{{HAIR}};border-radius:5px;position:relative'>"
                    & "<span style='position:absolute;top:0;bottom:0;right:0;border-radius:5px;background:" & _c & ";opacity:" & FORMAT ( 0.35 + 0.65 * DIVIDE ( ABS ( [@v] ), _maxAbs ), "0.00", "en-US" ) & ";width:" & FORMAT ( 100 * DIVIDE ( ABS ( [@v] ), _maxAbs ), "0", "en-US" ) & "%'></span></span>"
                    & "<b style='color:" & _c & "'>" & FORMAT ( [@v], "+$#,0;-$#,0", "en-US" ) & "</b></td>"
                & "<td style='{LEDGER_TD};text-align:right;color:" & IF ( [@w] >= 0.5, "{{LEAF6}}", "{{INK}}" ) & "'>" & FORMAT ( [@w], "0%" ) & "</td>"
                & "<td style='{LEDGER_TD};text-align:right'>" & IF ( ISBLANK ( [@r] ), "–", FORMAT ( [@r], "+0.00;-0.00", "en-US" ) & "R" ) & "</td>"
                & "<td style='{LEDGER_TD};text-align:right'>" & IF ( ISBLANK ( [@pf] ), "–", FORMAT ( [@pf], "0.00", "en-US" ) ) & "</td>"
                & "<td style='{LEDGER_TD};text-align:center'><span style='" & _pill & ";border-radius:11px;padding:3px 12px;font-size:12px;font-weight:800;letter-spacing:.04em'>" & UPPER ( [@s] ) & "</span></td>"
                & "</tr>",
            "", [@v], DESC ),
    "", [@v], DESC )
RETURN
    "<div style='font-family:{SANS};{TAB};background:#fff;border:1px solid {{HAIR}};border-radius:{RADIUS}px;height:900px;box-sizing:border-box;padding:20px 28px;overflow:auto;color:{{INK}};font-size:14px'>"
        & "<div style='display:flex;justify-content:space-between;align-items:baseline'><div style='font-family:{DISPLAY};font-size:23px;font-weight:700'>Strategy ledger</div>"
        & "<div style='font-size:13px;color:{{MUT}}'><b style='color:{{LEAF6}}'>EDGE</b> PF ≥ 1.2 on 10+ trades · <b style='color:#8A5A00'>WATCH</b> everything else · <b style='color:{{LOSS}}'>CUT</b> &lt; −$500 and PF &lt; 0.8</div></div>"
        & "<table style='width:100%;border-collapse:collapse;margin-top:12px'><tr>"
        & "<th style='{EYEBROW};color:{{MUT}};text-align:left;padding:10px 12px;border-bottom:2px solid {{INK}}'>Strategy</th>"
        & _th & "Trades</th>" & _th & "Net P&amp;L</th>" & _th & "Win</th>" & _th & "Avg R</th>" & _th & "PF</th>"
        & "<th style='{EYEBROW};color:{{MUT}};text-align:center;padding:10px 12px;border-bottom:2px solid {{INK}}'>Status</th></tr>"
        & _body & "</table></div>" """))

# ───────────────────────── 11 · alt text (bind in Format → General → Alt text → fx) ─────────────────────────
A = "11-alt-text"
m(A, "Alt - Account Equity", '"Account equity is " & FORMAT ( [Account Equity], "$#,0", "en-US" ) & ", " & FORMAT ( [Day P&L], "+$#,0;-$#,0", "en-US" ) & " today."')
m(A, "Alt - Net Closed P&L", '"Net closed P&L is " & FORMAT ( [Net P&L], "+$#,0;-$#,0", "en-US" ) & " across " & FORMAT ( [Trades], "#,0" ) & " trades."')
m(A, "Alt - Win Rate", '"Win rate is " & FORMAT ( [Win Rate], "0.0%" ) & ": " & [Wins] & " won and " & [Losses] & " lost."')
m(A, "Alt - Profit Factor", '"Profit factor is " & FORMAT ( [Profit Factor], "0.00", "en-US" ) & "; break-even is 1.00. Crypto alone is " & FORMAT ( [Crypto Profit Factor], "0.00", "en-US" ) & "."')
m(A, "Alt - Equity Curve", '"Line chart of cumulative closed P&L by day, ending at " & FORMAT ( [Net P&L], "$#,0;-$#,0", "en-US" ) & ", peak " & FORMAT ( [Peak P&L], "$#,0;-$#,0", "en-US" ) & ", low " & FORMAT ( [Low P&L], "$#,0;-$#,0", "en-US" ) & ", maximum drawdown " & FORMAT ( [Max Drawdown], "$#,0;-$#,0", "en-US" ) & "."')
m(A, "Alt - Waterfall", '"Waterfall: gross wins " & FORMAT ( [Gross Wins], "$#,0", "en-US" ) & ", stop exits " & FORMAT ( [Stop Exit P&L], "$#,0;-$#,0", "en-US" ) & ", other losses " & FORMAT ( [Other Losses], "$#,0;-$#,0", "en-US" ) & ", net " & FORMAT ( [Net P&L], "$#,0;-$#,0", "en-US" ) & "."')
m(A, "Alt - Asset Classes", '"Net P&L by asset class: crypto " & FORMAT ( [Crypto P&L], "+$#,0;-$#,0", "en-US" ) & ", equity " & FORMAT ( [Equity P&L], "+$#,0;-$#,0", "en-US" ) & ", options " & FORMAT ( [Options P&L], "+$#,0;-$#,0", "en-US" ) & "."')
m(A, "Alt - Shorts vs Longs", '"Shorts " & FORMAT ( [Short P&L], "+$#,0;-$#,0", "en-US" ) & " on " & [Short Trades] & " trades, " & FORMAT ( [Short Win Rate], "0%" ) & " win; longs " & FORMAT ( [Long P&L], "+$#,0;-$#,0", "en-US" ) & " on " & [Long Trades] & " trades, " & FORMAT ( [Long Win Rate], "0%" ) & " win."')
m(A, "Alt - Cover", '"Cover: The Book of a Paper Trader. Account equity " & FORMAT ( [Account Equity], "$#,0", "en-US" ) & ", net closed P&L " & FORMAT ( [Net P&L], "+$#,0;-$#,0", "en-US" ) & ", profit factor " & FORMAT ( [Profit Factor], "0.00", "en-US" ) & "."')
m(A, "Alt - Ledger", '"Table of " & FORMAT ( [Strategies], "0" ) & " strategies grouped by asset class with trades, net P&L, win rate, average R, profit factor and status."')

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

# ───────────────────────── design tokens → html/tokens.css + powerbi/trading-theme.json ─────────────────────────
import json
os.makedirs(os.path.join(ROOT, "html"), exist_ok=True)
css = ["/* Trading Analytics design tokens · generated by scripts/build_dax.py (same values as the DAX measures and the theme) */", ":root {"]
css += [f"  --color-{k.replace('_', '-')}: {v};" for k, v in SEM.items()]
css += [f"  --font-sans: {SANS};", f"  --font-display: {DISPLAY};", f"  --font-mono: {MONO};"]
css += [f"  --text-{k}: {v}px;" for k, v in TYPE.items()]
css += [f"  --radius-card: {RADIUS}px;", f"  --space: {SPACE}px;", "}", "",
        ".card { background: var(--color-surface); border: 1px solid var(--color-hairline); border-radius: var(--radius-card); padding: calc(var(--space) * 2.5) calc(var(--space) * 3); font-family: var(--font-sans); font-variant-numeric: tabular-nums; }",
        ".card--dark { background: var(--color-ink); color: #fff; border: 0; }",
        ".eyebrow { font-size: var(--text-eyebrow); font-weight: 700; letter-spacing: .09em; text-transform: uppercase; color: var(--color-neutral); }",
        ".kpi { font-size: var(--text-kpi); font-weight: 800; letter-spacing: -.025em; line-height: 1; }",
        ".title { font-family: var(--font-display); font-size: var(--text-title); font-weight: 700; }",
        ".gain { color: var(--color-gain); } .loss { color: var(--color-loss); }",
        ".pill { border-radius: 999px; padding: 3px 12px; font-size: var(--text-label); font-weight: 800; }",
        ".pill--edge { background: var(--color-mint); color: var(--color-gain); } .pill--cut { background: #FBE3E0; color: var(--color-loss); } .pill--watch { background: #FFF3DA; color: #8A5A00; }", ""]
open(os.path.join(ROOT, "html", "tokens.css"), "w").write("\n".join(css))

theme = {
  "name": "Trading Analytics · Forest (tokens)",
  "dataColors": [SEM["gain"], SEM["loss"], SEM["gain_bright"], SEM["loss_soft"], SEM["ink"], C["LEAF3"], SEM["neutral"], SEM["accent"]],
  "good": SEM["gain"], "bad": SEM["loss"], "neutral": SEM["neutral"],
  "maximum": SEM["gain"], "center": SEM["hairline"], "minimum": SEM["loss"],
  "background": SEM["surface"], "foreground": SEM["ink"], "tableAccent": SEM["gain"],
  "textClasses": {
    "title":   {"fontFace": "Georgia", "fontSize": 16, "color": SEM["ink"]},
    "header":  {"fontFace": "Segoe UI Semibold", "fontSize": 12, "color": SEM["ink"]},
    "label":   {"fontFace": "Segoe UI", "fontSize": 10, "color": SEM["neutral"]},
    "callout": {"fontFace": "Segoe UI Bold", "fontSize": 32, "color": SEM["ink"]}
  },
  "visualStyles": {
    "*": {"*": {
      "visualHeader": [{"show": False}],
      "border": [{"show": False}],
      "dropShadow": [{"show": False}],
      "visualTooltip": [{"background": {"solid": {"color": SEM["ink"]}}, "titleFontColor": {"solid": {"color": "#FFFFFF"}}, "valueFontColor": {"solid": {"color": "#FFFFFF"}}}]
    }},
    "page": {"*": {"background": [{"color": {"solid": {"color": SEM["canvas"]}}, "transparency": 0}],
                   "outspace": [{"color": {"solid": {"color": SEM["canvas"]}}}]}},
    "pageNavigator": {"*": {"fill": [{"show": False}], "text": [{"show": False}], "outline": [{"show": False}]}},
    "actionButton": {"*": {"fill": [{"show": False}], "outline": [{"show": False}], "text": [{"show": False}], "icon": [{"show": False}]}}
  }
}
open(os.path.join(ROOT, "powerbi", "trading-theme.json"), "w").write(json.dumps(theme, indent=2, ensure_ascii=False) + "\n")
print("tokens.css + theme written")
