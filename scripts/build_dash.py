import datetime as dt, math, sys, re

OUT_DIR, MODE = sys.argv[1], sys.argv[2]   # MODE: replica | guide
GUIDE = MODE == "guide"
MINUS = "−"
LEAF = "#2E9E44"; LEAF_L = "#4ED15A"; RED = "#E0574C"; RED_D = "#B5352B"; GREY = "#C9D2CA"; INK = "#0F1712"
MUT = "#6A746C"; BAND = "#EEF2EE"

RAW = """2026-08-27,2871
2026-08-31,-741
2026-09-01,-114
2026-09-02,-92
2026-09-03,-156
2026-09-04,-69
2026-09-05,-579
2026-09-06,64
2026-09-07,-20
2026-09-08,-2161
2026-09-09,-1146
2026-09-10,-954
2026-09-11,-1172
2026-09-13,14
2026-09-14,143
2026-09-15,-1760
2026-09-16,-28
2026-09-17,-1060
2026-09-18,31
2026-09-19,96
2026-09-20,-93
2026-09-21,-20
2026-09-22,1950
2026-09-23,222
2026-09-24,-14
2026-09-25,504
2026-09-26,85
2026-09-28,-221
2026-09-29,-44
2026-09-30,-231
2026-10-01,-204
2026-10-02,213
2026-10-03,145
2026-10-04,77
2026-10-05,10
2026-10-06,-168
2026-10-07,-1477
2026-10-08,-197
2026-10-09,169
2026-10-11,-94
2026-10-12,-19
2026-10-13,2085
2026-10-14,-402
2026-10-15,-324
2026-10-16,-931
2026-10-17,468
2026-10-18,5
2026-10-19,202
2026-10-20,-243
2026-10-21,-131
2026-10-22,-575
2026-10-23,568
2026-10-24,286
2026-10-26,355
2026-10-27,57
2026-10-28,-546
2026-10-29,665
2026-10-30,-4"""
PTS = [(dt.date.fromisoformat(a), int(b)) for a, b in (l.split(",") for l in RAW.split())]

def T(x, y, s, size=12, w=500, fill=INK, anchor="start", fam="Plus Jakarta Sans"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" font-weight="{w}" '
            f'fill="{fill}" text-anchor="{anchor}">{s}</text>')

def svg(w, h, inner, cls=""):
    return f'<svg class="{cls}" viewBox="0 0 {w} {h}" width="100%" xmlns="http://www.w3.org/2000/svg">{inner}</svg>'

def fm(v, sign=False):
    s = f"${abs(v):,.0f}"
    if v < 0: return MINUS + s
    return ("+" if sign and v > 0 else "") + s

# ---------- charts ----------
def equity_svg(W=900, H=250):
    d0 = dt.date(2026, 8, 26); last = dt.date(2026, 10, 30); span = (last - d0).days
    rows = [(d0, 0)]; c = 0
    for d, v in PTS:
        c += v; rows.append((d, c))
    X = lambda d: 56 + (d - d0).days / span * (W - 56 - 24)
    lo, hi = -10000, 4000; top, bot = 14, H - 42
    Y = lambda v: top + (hi - v) / (hi - lo) * (bot - top)
    pk = []; m = -10**9
    for _, c2 in rows:
        m = max(m, c2); pk.append(m)
    o = []
    for v, lab in [(4000, "+$4K"), (0, "$0"), (-4000, MINUS + "$4K"), (-8000, MINUS + "$8K")]:
        o.append(f'<line x1="56" x2="{W}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{"#CFD6CF" if v == 0 else "#E6EBE6"}" stroke-width="1"/>')
        o.append(T(0, Y(v) + 4, lab, 11, 500, MUT))
    poly = [(X(d), Y(p)) for (d, _), p in zip(rows, pk)] + [(X(d), Y(c2)) for d, c2 in rows][::-1]
    o.append('<polygon points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in poly) + f'" fill="{RED}" fill-opacity="0.16"/>')
    path = " ".join(("M" if i == 0 else "L") + f"{X(d):.1f},{Y(c2):.1f}" for i, (d, c2) in enumerate(rows))
    o.append(f'<path d="{path}" fill="none" stroke="{LEAF}" stroke-width="2" stroke-linejoin="round"/>')
    px, py = X(rows[1][0]), Y(2871); tr = min(rows, key=lambda r: r[1]); tx, ty = X(tr[0]), Y(tr[1])
    ex, ey = X(last), Y(-4711)
    o.append(f'<line x1="{tx:.1f}" x2="{tx:.1f}" y1="{py:.1f}" y2="{ty:.1f}" stroke="{RED}" stroke-dasharray="4 3"/>')
    o.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="#fff" stroke="{LEAF}" stroke-width="2"/>')
    o.append(T(px + 10, py - 8, "Peak +$2,871", 11, 700, LEAF))
    o.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="4" fill="#fff" stroke="{RED}" stroke-width="2"/>')
    o.append(T(tx + 8, ty + 4, "Low " + MINUS + "$6,960", 11, 700, RED_D))
    o.append(T(tx - 6, (py + ty) / 2, MINUS + "$9,831", 11, 700, RED_D, "end"))
    o.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="5" fill="{LEAF}"/>')
    o.append(T(ex - 8, ey - 10, MINUS + "$4,711", 12, 700, INK, "end"))
    for s, lab in [("2026-09-01", "1 Sep"), ("2026-09-15", "15 Sep"), ("2026-10-01", "1 Oct"), ("2026-10-15", "15 Oct"), ("2026-10-29", "29 Oct")]:
        o.append(T(X(dt.date.fromisoformat(s)), H - 10, lab, 11, 500, MUT, "middle"))
    return svg(W, H, "".join(o))

def dd_mini(W=400, H=78):
    d0 = dt.date(2026, 8, 26); span = (dt.date(2026, 10, 30) - d0).days
    rows = [(d0, 0)]; c = 0
    for d, v in PTS:
        c += v; rows.append((d, c))
    X = lambda d: (d - d0).days / span * W
    Y = lambda v: 8 + (-v) / 10000 * (H - 24)
    m = 0; dd = []
    for d, c2 in rows:
        m = max(m, c2); dd.append((d, c2 - m))
    line = " ".join(("M" if i == 0 else "L") + f"{X(d):.1f} {Y(-v):.1f}" for i, (d, v) in enumerate(dd))
    area = line + f" L{W} 8 L0 8 Z"
    lo = min(dd, key=lambda r: r[1])
    o = [f'<line x1="0" y1="8" x2="{W}" y2="8" stroke="#9CC9A0"/>',
         f'<path d="{area}" fill="{RED}" fill-opacity="0.16"/>',
         f'<path d="{line}" fill="none" stroke="{RED}" stroke-width="1.8" stroke-linejoin="round"/>',
         f'<circle cx="{X(lo[0]):.1f}" cy="{Y(-lo[1]):.1f}" r="4" fill="{RED}" stroke="#D9EED9" stroke-width="2"/>',
         T(X(lo[0]) + 8, Y(-lo[1]) + 4, "17 Sep", 10, 700, RED_D),
         T(0, H - 2, "27 Aug", 10, 500, "#4E6553"),
         T(W, H - 2, "30 Oct · " + MINUS + "$7.6K below peak", 10, 500, "#4E6553", "end")]
    return svg(W, H, "".join(o))

def waterfall_svg(W=900, H=200):
    x0, x1 = 230, W - 70; vmin, vmax = -6000, 26000
    SX = lambda v: x0 + (v - vmin) / (vmax - vmin) * (x1 - x0)
    rows = [("Gross wins", 0, 23859, LEAF, "+$23,859", LEAF),
            ("Stop exits", 23859, 10887, RED, MINUS + "$12,972", RED_D),
            ("Other losses", 10887, -4711, "#F2B5AE", MINUS + "$15,598", RED_D),
            ("Net result", 0, -4711, INK, MINUS + "$4,711", INK)]
    o = []
    for i, (lab, a, b, col, val, vc) in enumerate(rows):
        y = 8 + i * 46
        xa, xb = sorted([SX(a), SX(b)])
        o.append(T(0, y + 16, lab, 12, 600, INK))
        o.append(f'<rect x="{xa:.1f}" y="{y:.1f}" width="{xb - xa:.1f}" height="26" rx="5" fill="{col}"/>')
        o.append(T(W, y + 18, val, 12, 700, vc, "end"))
    z = SX(0)
    o.append(f'<line x1="{z:.1f}" x2="{z:.1f}" y1="0" x2="{z:.1f}" y2="{H - 22}" stroke="{INK}"/>')
    for v, lab in [(0, "$0"), (10000, "$10K"), (20000, "$20K")]:
        o.append(T(SX(v), H - 6, lab, 10, 500, MUT, "middle"))
    return svg(W, H, "".join(o))

def crypto_weeks_svg(W=400, H=86):
    c = [0, -555, -475, 180, 591, 784, -383, 445, -219, 262]; e = [2871, -793, -4556, -1756, 2041, 6, -1210, 435, 326, 266]
    cc = []; ce = []; a = b = 0
    for x, y in zip(c, e):
        a += x; b += y; cc.append(a); ce.append(b)
    lo_, hi_ = -4800, 3200
    Y = lambda v: 6 + (hi_ - v) / (hi_ - lo_) * (H - 14)
    X = lambda i: i * (W - 70) / 9
    pl = lambda arr: " ".join(("M" if i == 0 else "L") + f"{X(i):.1f} {Y(v):.1f}" for i, v in enumerate(arr))
    o = [f'<line x1="0" y1="{Y(0):.1f}" x2="{W - 70}" y2="{Y(0):.1f}" stroke="rgba(255,255,255,.2)" stroke-dasharray="3 3"/>',
         f'<path d="{pl(ce)}" fill="none" stroke="{RED}" stroke-width="2" stroke-linejoin="round"/>',
         f'<path d="{pl(cc)}" fill="none" stroke="{LEAF_L}" stroke-width="2.4" stroke-linejoin="round"/>',
         f'<circle cx="{X(9):.1f}" cy="{Y(cc[-1]):.1f}" r="4" fill="{LEAF_L}"/>',
         f'<circle cx="{X(9):.1f}" cy="{Y(ce[-1]):.1f}" r="4" fill="{RED}"/>',
         T(X(9) + 9, Y(cc[-1]) + 4, "Crypto", 11, 700, LEAF_L),
         T(X(9) + 9, Y(ce[-1]) + 4, "Equity", 11, 700, "#FF8F85")]
    return svg(W, H, "".join(o))

def lollipop_svg(W=900, H=232):
    data = [("equity-one-dissent-half", 1282, 19), ("equity-hourly-close-xc1", 1232, 5), ("short-ma99-break", 806, 18),
            ("long-pullback", 438, 86), ("option-debit-spread", -973, 12), ("equity-legacy-untagged", -1679, 22),
            ("equity-swing-long", -1864, 11), ("option-legacy-untagged", -2000, 19)]
    x0, x1 = 232, W - 40; lo, hi = -2200, 1400
    SX = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    z = SX(0); rh = 25; top = 4; o = []
    o.append(f'<line x1="{z:.1f}" x2="{z:.1f}" y1="0" y2="{top + 8 * rh}" stroke="{INK}"/>')
    for v in [-2000, -1000, 1000]:
        o.append(f'<line x1="{SX(v):.1f}" x2="{SX(v):.1f}" y1="0" y2="{top + 8 * rh}" stroke="#E6EBE6" stroke-dasharray="2 3"/>')
        o.append(T(SX(v), H - 4, fm(v, True), 10, 500, MUT, "middle"))
    for i, (n, v, c) in enumerate(data):
        y = top + i * rh + 12; col = LEAF if v > 0 else RED; r = 4 + math.sqrt(c) * 0.9
        o.append(T(0, y + 4, n, 11, 500, INK, fam="Geist Mono, monospace"))
        o.append(f'<line x1="{z:.1f}" x2="{SX(v):.1f}" y1="{y}" y2="{y}" stroke="{col}" stroke-width="2"/>')
        o.append(f'<circle cx="{SX(v):.1f}" cy="{y}" r="{r:.1f}" fill="{col}" stroke="#fff" stroke-width="1.2"/>')
        if v > 0: o.append(T(SX(v) + r + 6, y + 4, fm(v, True), 11, 700, col))
        else: o.append(T(SX(v) - r - 6, y + 4, fm(v, True), 11, 700, col, "end"))
    return svg(W, H, "".join(o))

def rdots_svg(W=900, H=190):
    bins = [("−2.5", 2), ("−2", 1), ("−1.5", 37), ("−1", 44), ("−0.5", 11), ("0", 33), ("+0.5", 21), ("+1", 24), ("+1.5", 18), ("+2", 4), ("+2.5", 3), ("+3", 2)]
    cw = W / len(bins); B = 150; r = 4.6; dx = 11.5; dy = 11.5; o = []
    for i, (lab, n) in enumerate(bins):
        col = RED if i <= 2 else (GREY if i <= 6 else LEAF)
        cx = cw * (i + 0.5)
        for k in range(n):
            row, c = divmod(k, 4)
            o.append(f'<circle cx="{cx + (c - 1.5) * dx:.1f}" cy="{B - r - row * dy:.1f}" r="{r}" fill="{col}"/>')
        top = B - r - math.ceil(n / 4) * dy
        o.append(T(cx, top - 6, str(n), 11, 700, INK, "middle"))
        o.append(T(cx, B + 18, lab + "R", 10, 500, MUT, "middle"))
    o.append(f'<line x1="0" x2="{W}" y1="{B + 6}" y2="{B + 6}" stroke="{INK}"/>')
    sx = cw * 3; bx = cw * 5
    o.append(f'<line x1="{sx:.1f}" x2="{sx:.1f}" y1="8" y2="{B + 6}" stroke="{INK}" stroke-dasharray="3 3"/>')
    o.append(T(sx - 6, 14, "PLANNED STOP", 10, 700, INK, "end"))
    o.append(f'<line x1="{bx:.1f}" x2="{bx:.1f}" y1="8" y2="{B + 6}" stroke="#CFD6CF"/>')
    o.append(T(bx + 6, 14, "BREAK-EVEN", 10, 600, MUT))
    return svg(W, H, "".join(o))

def units_svg(W=400, H=70):
    o = []
    for r, (n, wn, ls) in enumerate([("Short", 71, 43), ("Long", 107, 134)]):
        y = r * 36; x = 56
        o.append(T(0, y + 12, n, 11, 600, "#DDE9DF"))
        for k in range(round(wn / 5)):
            o.append(f'<rect x="{x:.1f}" y="{y + 2}" width="6" height="13" rx="1.5" fill="{LEAF_L}"/>'); x += 7.4
        x += 4
        for k in range(round(ls / 5)):
            o.append(f'<rect x="{x:.1f}" y="{y + 2}" width="6" height="13" rx="1.5" fill="{RED}"/>'); x += 7.4
        o.append(T(56, y + 30, f"{wn} won · {ls} lost", 9, 500, "#8FA594"))
    return svg(W, H, "".join(o))

def treemap_svg():
    return ('<svg class="tm" viewBox="0 0 900 214" width="100%" xmlns="http://www.w3.org/2000/svg">'
            '<rect x="1.5" y="1.5" width="346.2" height="211" rx="10" fill="#2E9E44"/>'
            '<text x="14" y="30" font-family="Plus Jakarta Sans" font-size="20" font-weight="600" fill="#FFFFFF">KO</text>'
            '<text x="14" y="52" font-family="Plus Jakarta Sans" font-size="13" fill="#D7F5DA">$9,522 · 39%</text>'
            '<text x="337" y="202" font-family="Plus Jakarta Sans" font-size="22" font-weight="800" fill="#FFFFFF" text-anchor="end">+2.53%</text>'
            '<rect x="350.7" y="1.5" width="171.5" height="211" rx="10" fill="#E0574C"/>'
            '<text x="363" y="24" font-family="Plus Jakarta Sans" font-size="14" font-weight="600" fill="#FFFFFF">PANW</text>'
            '<text x="363" y="42" font-family="Plus Jakarta Sans" font-size="11" fill="#FFE1DD">$4,757 · 19%</text>'
            '<text x="512" y="202" font-family="Plus Jakarta Sans" font-size="13" font-weight="800" fill="#FFFFFF" text-anchor="end">−1.99%</text>'
            '<rect x="525.2" y="1.5" width="120.9" height="211" rx="10" fill="#BDE8C1"/>'
            '<text x="537.7" y="24" font-family="Plus Jakarta Sans" font-size="14" font-weight="600" fill="#0F1712">DE</text>'
            '<text x="537.7" y="42" font-family="Plus Jakarta Sans" font-size="11" fill="#2E6B3A">$3,377 · 14%</text>'
            '<text x="635.5" y="202" font-family="Plus Jakarta Sans" font-size="13" font-weight="800" fill="#0F1712" text-anchor="end">+0.80%</text>'
            '<rect x="649" y="1.5" width="185.1" height="109.3" rx="10" fill="#BDE8C1"/>'
            '<text x="661.5" y="24" font-family="Plus Jakarta Sans" font-size="14" font-weight="600" fill="#0F1712">MRK</text>'
            '<text x="661.5" y="42" font-family="Plus Jakarta Sans" font-size="11" fill="#2E6B3A">$2,691 · 11%</text>'
            '<text x="823.6" y="100" font-family="Plus Jakarta Sans" font-size="13" font-weight="800" fill="#0F1712" text-anchor="end">+1.10%</text>'
            '<rect x="649" y="113.8" width="185.1" height="98.7" rx="10" fill="#BDE8C1"/>'
            '<text x="661.5" y="136" font-family="Plus Jakarta Sans" font-size="14" font-weight="600" fill="#0F1712">DIS</text>'
            '<text x="661.5" y="154" font-family="Plus Jakarta Sans" font-size="11" fill="#2E6B3A">$2,438 · 10%</text>'
            '<text x="823.6" y="202" font-family="Plus Jakarta Sans" font-size="13" font-weight="800" fill="#0F1712" text-anchor="end">+0.97%</text>'
            '<rect x="837.1" y="1.5" width="61.4" height="211" rx="10" fill="#F6CFCA"/>'
            '<text x="849.6" y="24" font-family="Plus Jakarta Sans" font-size="14" font-weight="600" fill="#0F1712">CRWD</text>'
            '<text x="849.6" y="42" font-family="Plus Jakarta Sans" font-size="11" fill="#9A2E25">$1.8K</text>'
            '<text x="888" y="202" font-family="Plus Jakarta Sans" font-size="13" font-weight="800" fill="#0F1712" text-anchor="end">−0.39%</text>'
            '</svg>')

def sankey_svg(sells_note):
    return ('<svg viewBox="0 0 900 150" width="100%" xmlns="http://www.w3.org/2000/svg">'
            '<path d="M120 1 C270 1 270 1 420 1 L420 30.05 C270 30.05 270 30.05 120 30.05 Z" fill="#7FA488" fill-opacity="0.35"/>'
            '<path d="M120 30.05 C270 30.05 270 36.05 420 36.05 L420 130.61 C270 130.61 270 124.61 120 124.61 Z" fill="#7FA488" fill-opacity="0.35"/>'
            '<path d="M120 124.61 C270 124.61 270 136.61 420 136.61 L420 143 C270 143 270 131 120 131 Z" fill="#7FA488" fill-opacity="0.35"/>'
            '<path d="M430 1 C575 1 575 1 720 1 L720 24.9 C575 24.9 575 24.9 430 24.9 Z" fill="#2E9E44" fill-opacity="0.45"/>'
            '<path d="M430 24.9 C575 24.9 575 64.07 720 64.07 L720 68.81 C575 68.81 575 29.64 430 29.64 Z" fill="#9AA59C" fill-opacity="0.45"/>'
            '<path d="M430 29.64 C575 29.64 575 137.23 720 137.23 L720 137.64 C575 137.64 575 30.05 430 30.05 Z" fill="#E0574C" fill-opacity="0.45"/>'
            '<path d="M430 36.05 C575 36.05 575 24.9 720 24.9 L720 54.77 C575 54.77 575 65.92 430 65.92 Z" fill="#2E9E44" fill-opacity="0.45"/>'
            '<path d="M430 65.92 C575 65.92 575 68.81 720 68.81 L720 129.79 C575 129.79 575 126.9 430 126.9 Z" fill="#9AA59C" fill-opacity="0.45"/>'
            '<path d="M430 126.9 C575 126.9 575 137.64 720 137.64 L720 138.88 C575 138.88 575 128.14 430 128.14 Z" fill="#E0574C" fill-opacity="0.45"/>'
            '<path d="M430 128.14 C575 128.14 575 146.32 720 146.32 L720 148.79 C575 148.79 575 130.61 430 130.61 Z" fill="#C9D2CA" fill-opacity="0.45"/>'
            '<path d="M430 136.61 C575 136.61 575 54.77 720 54.77 L720 58.07 C575 58.07 575 139.91 430 139.91 Z" fill="#2E9E44" fill-opacity="0.45"/>'
            '<path d="M430 139.91 C575 139.91 575 129.79 720 129.79 L720 131.23 C575 131.23 575 141.35 430 141.35 Z" fill="#9AA59C" fill-opacity="0.45"/>'
            '<path d="M430 141.35 C575 141.35 575 138.88 720 138.88 L720 140.32 C575 140.32 575 142.79 430 142.79 Z" fill="#E0574C" fill-opacity="0.45"/>'
            '<path d="M430 142.79 C575 142.79 575 148.79 720 148.79 L720 149 C575 149 575 143 430 143 Z" fill="#C9D2CA" fill-opacity="0.45"/>'
            '<rect x="110" y="1" width="10" height="130" rx="2" fill="#0F1712"/>'
            '<rect x="420" y="1" width="10" height="29" rx="2" fill="#0F1712"/>'
            '<rect x="420" y="36" width="10" height="94.6" rx="2" fill="#0F1712"/>'
            '<rect x="420" y="136.6" width="10" height="6.4" rx="2" fill="#0F1712"/>'
            '<rect x="720" y="1" width="10" height="57.1" rx="2" fill="#2E9E44"/>'
            '<rect x="720" y="64.1" width="10" height="67.2" rx="2" fill="#9AA59C"/>'
            '<rect x="720" y="137.2" width="10" height="3.1" rx="2" fill="#E0574C"/>'
            '<rect x="720" y="146.3" width="10" height="2.7" rx="2" fill="#C9D2CA"/>'
            '<text x="100" y="62" font-family="Plus Jakarta Sans" font-size="22" font-weight="800" fill="#0F1712" text-anchor="end">631</text>'
            '<text x="100" y="80" font-family="Plus Jakarta Sans" font-size="11" fill="#6A746C" text-anchor="end">orders</text>'
            '<text x="412" y="19.5" font-family="Plus Jakarta Sans" font-size="12" font-weight="600" fill="#0F1712" text-anchor="end">Buy 141</text>'
            '<text x="412" y="87.3" font-family="Plus Jakarta Sans" font-size="12" font-weight="600" fill="#0F1712" text-anchor="end">Sell 459</text>'
            '<text x="412" y="143.8" font-family="Plus Jakarta Sans" font-size="12" font-weight="600" fill="#0F1712" text-anchor="end">Other 31</text>'
            '<text x="742" y="28" font-family="Plus Jakarta Sans" font-size="13" font-weight="700" fill="#2E9E44">Filled 277</text>'
            '<text x="742" y="42" font-family="Plus Jakarta Sans" font-size="11" fill="#6A746C">44% of orders</text>'
            '<text x="742" y="88" font-family="Plus Jakarta Sans" font-size="13" font-weight="700" fill="#6A746C">Canceled 326</text>'
            f'<text x="742" y="102" font-family="Plus Jakarta Sans" font-size="11" fill="#6A746C">{sells_note}</text>'
            '<text x="742" y="131" font-family="Plus Jakarta Sans" font-size="13" font-weight="700" fill="#E0574C">Expired 15 · Working 13</text>'
            '<text x="742" y="146" font-family="Plus Jakarta Sans" font-size="11" fill="#6A746C">4% left open or lapsed</text>'
            '</svg>')

def donut():
    C = 2 * math.pi * 44; inv = 24540 / 95819
    return ('<svg width="94" height="94" viewBox="0 0 112 112" fill="none">'
            '<circle cx="56" cy="56" r="44" stroke="#C3E2C4" stroke-width="14"/>'
            f'<circle cx="56" cy="56" r="44" stroke="#2E9E44" stroke-width="14" stroke-dasharray="{C*inv:.1f} {C:.1f}" stroke-linecap="round" transform="rotate(-90 56 56)"/>'
            '<text x="56" y="56" font-family="Plus Jakarta Sans" font-size="18" font-weight="800" fill="#0F1712" text-anchor="middle">26%</text>'
            '<text x="56" y="71" font-family="Plus Jakarta Sans" font-size="9" font-weight="600" fill="#4E6553" text-anchor="middle">INVESTED</text></svg>')

# ---------- UI pieces ----------
ICON = {
 "wallet": '<rect x="3" y="5.5" width="15" height="11" rx="2.5"/><path d="M13 11h4.5"/><path d="M5 5.5 L13 2.8 L14 5.5"/>',
 "down": '<path d="M3 6 L8 11 L11 8 L17 14"/><path d="M13 14h4v-4"/>',
 "target": '<circle cx="10" cy="10" r="7"/><circle cx="10" cy="10" r="3"/>',
 "scale": '<path d="M10 3v14M6 17h8M4 6.5h12"/><path d="M4 6.5 L2 11.5h4Z"/><path d="M16 6.5 L14 11.5h4Z"/>',
 "sigma": '<path d="M14 4H6l5 6-5 6h8"/>',
 "warn": '<path d="M10 3 L18 17H2Z"/><path d="M10 8v4M10 14.6v.2"/>',
 "trophy": '<path d="M6 3h8v5a4 4 0 0 1-8 0Z"/><path d="M10 12v3M7 17h6M6 5H3v1a3 3 0 0 0 3 3M14 5h3v1a3 3 0 0 1-3 3"/>',
 "stop": '<circle cx="10" cy="10" r="7.5"/><path d="M6.5 10h7"/>',
 "pie": '<path d="M10 2.5a7.5 7.5 0 1 0 7.5 7.5H10Z"/><path d="M12.5 2.8a7.5 7.5 0 0 1 4.7 4.7h-4.7Z"/>',
 "check": '<circle cx="10" cy="10" r="7.5"/><path d="M6.5 10.2 L9 12.5 L13.5 7.8"/>',
 "refresh": '<path d="M16 8a6.5 6.5 0 0 0-11.5-2.5M4 12a6.5 6.5 0 0 0 11.5 2.5"/><path d="M4.5 2.5v3h3M15.5 17.5v-3h-3"/>',
 "up": '<path d="M3 14 L8 9 L11 12 L17 6"/><path d="M13 6h4v4"/>',
 "trend": '<path d="M3 14 L8 9 L11 12 L17 6"/><path d="M13 6h4v4"/>',
 "bars": '<rect x="4" y="10" width="3" height="7" rx="1"/><rect x="9" y="6" width="3" height="11" rx="1"/><rect x="14" y="3" width="3" height="14" rx="1"/>',
 "clock": '<circle cx="10" cy="10" r="7.5"/><path d="M10 6v4l3 2"/>',
 "bolt": '<path d="M11 2 L4 11h5l-1 7 7-9h-5z"/>',
 "tag": '<path d="M3 3h7l7 7-7 7-7-7z"/><circle cx="7" cy="7" r="1.2"/>',
 "book": '<path d="M3 5c3-1 6-1 7 1 1-2 4-2 7-1v11c-3-1-6-1-7 1-1-2-4-2-7-1z"/><path d="M10 6v11"/>',
}
def badge(icon, bg, fg):
    return (f'<div class="badge" style="background:{bg}"><svg width="20" height="20" viewBox="0 0 20 20" fill="none" '
            f'stroke="{fg}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{ICON[icon]}</svg></div>')

def mini_bars(bars, w=10, gap=5):
    out = f'<div class="mb" style="display:flex;gap:{gap}px;align-items:flex-end;height:48px">'
    for h, col in bars:
        out += f'<div style="width:{w}px;height:{h}px;border-radius:3px;background:{col}"></div>'
    return out + "</div>"

def kpi(label, value, sub, bars, icon, dark=False, vcol=None, badge_bg="#EEF2EE", badge_fg=INK, pill=None, extra_val=""):
    card_bg = "linear-gradient(135deg,#0E2215 0%,#16331F 100%)" if dark else "#FFFFFF"
    lc = "#A6BBAA" if dark else MUT
    vc = vcol or ("#FFFFFF" if dark else INK)
    sc = "#8FA594" if dark else MUT
    pill_html = ""
    if pill:
        pbg, pfg, ptxt = pill
        pill_html = f'<span style="padding:2px 8px;border-radius:20px;background:{pbg};font-weight:700;font-size:11px;color:{pfg}">{ptxt}</span> '
    if dark:
        badge_bg = "rgba(78,209,90,.14)"; badge_fg = LEAF_L
    return (f'<div class="card kpi" style="flex:1;background:{card_bg};padding:20px 22px;display:flex;justify-content:space-between;align-items:flex-end">'
            f'<div style="display:flex;flex-direction:column;height:100%;justify-content:space-between">'
            f'<div style="font-weight:600;font-size:13px;color:{lc}">{label}</div>'
            f'<div class="val" style="font-weight:800;font-size:36px;line-height:38px;letter-spacing:-.03em;color:{vc}">{value}{extra_val}</div>'
            f'<div style="font-size:11px;color:{sc};display:flex;align-items:center;gap:6px">{pill_html}{sub}</div></div>'
            f'<div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px">{mini_bars(bars) if bars else ""}</div>'
            f'{badge(icon, badge_bg, badge_fg)}</div>')

def card(title, sub, body, pill="", legend="", style="", cls="white"):
    bg = "#FFFFFF" if cls == "white" else ""
    head = (f'<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px">'
            f'<div><div style="font-weight:700;font-size:18px;color:{INK}">{title}</div>'
            f'<div style="font-size:12px;color:{MUT};margin-top:2px">{sub}</div></div>'
            f'<div style="display:flex;gap:10px;align-items:center">{legend}{pill}</div></div>')
    return (f'<div class="card" style="flex:1;padding:20px 26px 18px;display:flex;flex-direction:column;justify-content:space-between;background:#FFFFFF;{style}">'
            f'{head}{body}</div>')

def dark_card(title, pill, body, footer="", style=""):
    head = (f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'<div style="font-weight:700;font-size:18px;color:#FFFFFF">{title}</div>{pill}</div>')
    return (f'<div class="card" style="flex:1;padding:22px 26px;display:flex;flex-direction:column;justify-content:space-between;'
            f'background:linear-gradient(160deg,#0E2215 0%,#123A1E 100%);color:#FFFFFF;{style}">{head}{body}'
            f'<div style="font-size:12px;color:#8FA594">{footer}</div></div>')

def mint_card(big, big_col, line_html, body, style=""):
    return (f'<div class="card" style="flex:1;padding:24px 26px;display:flex;flex-direction:column;justify-content:space-between;background:#D9EED9;{style}">'
            f'<div><div style="font-weight:800;font-size:52px;line-height:54px;letter-spacing:-.04em;color:{big_col}">{big}</div>'
            f'<div style="display:flex;align-items:center;gap:6px;margin-top:6px;font-weight:600;font-size:14px;color:#1F3A26">{line_html}</div></div>'
            f'{body}</div>')

def row_icon(icon, text, sub, fg=LEAF):
    return (f'<div style="display:flex;align-items:center;gap:14px"><div style="width:42px;height:42px;flex-shrink:0;border-radius:50%;background:#C3E2C4;display:flex;align-items:center;justify-content:center">'
            f'<svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="{fg}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICON[icon]}</svg></div>'
            f'<div style="display:flex;flex-direction:column"><div style="font-weight:700;font-size:16px;color:#0F1712">{text}</div>'
            f'<div style="font-size:12px;color:#4E6553">{sub}</div></div></div>')

def pill(text, bg="#F5E9E1", fg=RED_D):
    return f'<span style="padding:6px 12px;border-radius:20px;background:{bg};font-weight:700;font-size:12px;color:{fg};white-space:nowrap">{text}</span>'

def rail(active):
    items = [("Book", "book", "M3 17 L8 11 L12 14 L19 5|M3 19 H19"), ("Edge", "edge", "C|R"), ("Desk", "desk", "D")]
    def ic(kind, col):
        if kind == "Book":
            return f'<path d="M3 17 L8 11 L12 14 L19 5" stroke="{col}" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/><path d="M3 19 H19" stroke="{col}" stroke-width="1.9" stroke-linecap="round"/>'
        if kind == "Edge":
            return f'<circle cx="11" cy="11" r="8" stroke="{col}" stroke-width="1.9"/><circle cx="11" cy="11" r="3.5" stroke="{col}" stroke-width="1.9"/>'
        return f'<rect x="3" y="4" width="16" height="14" rx="3" stroke="{col}" stroke-width="1.9"/><path d="M3 9 H19 M9 9 V18" stroke="{col}" stroke-width="1.9"/>'
    html = ('<div class="rail"><div class="logo"><svg width="24" height="24" viewBox="0 0 24 24" fill="none">'
            '<path d="M4 17 L9 11 L13 14 L20 6" stroke="#0B1A10" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg></div>'
            '<div style="display:flex;flex-direction:column;gap:14px;align-items:center;flex-grow:1">')
    for name, key, _ in items:
        on = name == active
        bg = LEAF_L if on else "transparent"; col = "#0B1A10" if on else "#8FA594"
        fw = 700 if on else 600
        html += (f'<div class="nav" style="background:{bg}"><svg width="22" height="22" viewBox="0 0 22 22" fill="none">{ic(name, col)}</svg>'
                 f'<div style="font-weight:{fw};font-size:10px;color:{col}">{name}</div></div>')
    html += ('</div><div style="display:flex;flex-direction:column;align-items:center;gap:6px">'
             '<div style="width:8px;height:8px;border-radius:50%;background:#4ED15A;box-shadow:0 0 0 4px rgba(78,209,90,.18)"></div>'
             '<div style="font-weight:600;font-size:9px;letter-spacing:.12em;color:#8FA594">PAPER</div></div></div>')
    return html

def header(title, dek, pills):
    p = "".join(pills)
    return (f'<div class="head"><div style="display:flex;flex-direction:column;gap:2px">'
            f'<div class="h-title" style="font-weight:800;font-size:30px;line-height:36px;letter-spacing:-.02em;color:{INK}">{title}</div>'
            f'<div style="font-weight:500;font-size:13px;color:{MUT}">{dek}</div></div>'
            f'<div style="display:flex;gap:10px;align-items:center">{p}</div></div>')

def hpill(text, dark=False):
    if dark:
        return (f'<div style="display:flex;align-items:center;gap:8px;height:40px;padding:0 16px;border-radius:12px;background:#101511">'
                f'<div style="font-weight:600;font-size:13px;color:#FFFFFF">{text}</div>'
                f'<svg width="10" height="10" viewBox="0 0 10 10"><path d="M2 3.5 L5 6.5 L8 3.5" stroke="#FFFFFF" stroke-width="1.5" fill="none"/></svg></div>')
    return (f'<div style="display:flex;align-items:center;gap:8px;height:40px;padding:0 14px;border-radius:12px;background:#FFFFFF;border:1px solid #E3E8E3">'
            f'<div style="width:8px;height:8px;border-radius:50%;background:#4ED15A"></div>'
            f'<div style="font-weight:600;font-size:13px;color:{INK}">{text}</div></div>')

def footer_row(note, src, n):
    return ""

def frame(inner):
    return f'<section class="wrap"><div class="board">{inner}</div></section>'

# ---------- pages ----------
def page_book():
    kpis = ('<div class="kpis" style="display:flex;gap:18px;height:138px;flex-shrink:0">'
            + kpi("Account equity", "$95,819", pill(MINUS + "$456", "rgba(224,87,76,.18)", "#FF8F85") + " today",
                  [(46, RED), (23, LEAF_L), (4, LEAF_L), (14, LEAF_L)], "wallet", dark=True)
            + kpi("Net closed P&amp;L", MINUS + "$4,711", "crypto · equity · options",
                  [(10, LEAF), (37, RED), (46, RED)], "down", vcol=RED, badge_bg="#FCE7E5", badge_fg=RED_D)
            + kpi("Win rate", "50.1", "178 won · 177 lost", [(46, LEAF), (39, GREY), (36, GREY)], "target",
                  extra_val='<span style="font-weight:500;font-size:20px;color:#6A746C">%</span>')
            + kpi("Profit factor", "0.84", "only crypto clears 1.0 (1.14)", [(46, LEAF), (34, RED), (28, RED)], "scale",
                  extra_val='<span style="font-weight:500;font-size:16px;color:#6A746C"> / 1.00</span>')
            + '</div>')
    eq = card("Equity curve &amp; drawdown", "Cumulative closed P&amp;L by day · shaded = distance below the running peak",
              f'<div style="margin-top:8px">{equity_svg()}</div>',
              pill=('<span style="padding:6px 12px;border-radius:9px;background:#101511;font-weight:600;font-size:12px;color:#FFFFFF">Daily</span>'
                    '<span style="padding:6px 12px;border-radius:9px;font-weight:600;font-size:12px;color:#6A746C">Weekly</span>'))
    right = mint_card(MINUS + "$9,831", INK, "max drawdown from the 27 Aug peak",
        '<div style="display:flex;flex-direction:column;gap:14px">'
        + row_icon("down", "September " + MINUS + "$6,828", "168 trades · 46% win · the bleed", RED_D)
        + row_icon("check", "October " + MINUS + "$13", "184 trades · 54% win · bleeding stopped")
        + '</div>')
    row2 = f'<div class="row2" style="display:flex;gap:18px;flex:1.2">{eq}<div style="flex:1;display:flex">{right}</div></div>'
    row2 = row2.replace('<div style="flex:1;display:flex">' + right + '</div>', right)
    wf = card("From $23.9K won to $4.7K lost", "P&amp;L waterfall · stop exits alone erase more than half of all gains",
              f'<div style="margin-top:6px">{waterfall_svg()}</div>', pill=pill("Stops = 54% of gains"))
    crypto = dark_card("Only crypto pays", '<span style="padding:5px 10px;border-radius:10px;background:#FFFFFF;font-weight:600;font-size:11px;color:#0F1712">By asset</span>',
        '<div style="font-size:11px;color:#8FA594;margin-top:6px">Cumulative P&amp;L by week</div>'
        + crypto_weeks_svg()
        + ''.join(f'<div style="display:flex;align-items:center;gap:12px"><div style="width:56px;flex-shrink:0;font-weight:600;font-size:12px">{n}</div>'
                  f'<div style="flex:1;height:8px;border-radius:4px;background:rgba(255,255,255,.08)"><div style="width:{w}%;height:8px;border-radius:4px;background:{c}"></div></div>'
                  f'<div style="width:66px;text-align:right;font-weight:800;font-size:13px;color:{tc}">{v}</div></div>'
                  for n, w, c, tc, v in [("Crypto", 21, LEAF_L, LEAF_L, "+$630"), ("Equity", 80, RED, "#FF8F85", MINUS + "$2,369"), ("Options", 100, RED, "#FF8F85", MINUS + "$2,973")]),
        "233 crypto trades · 53% win · PF 1.14")
    row3 = f'<div class="row3" style="display:flex;gap:18px;flex:1">{wf}{crypto}</div>'
    return ("<div class=\"main\">" + header("The Book", "Is the account growing? · 355 closed trades · 27 Aug – 30 Oct 2026",
                                           [hpill("Alpaca · Paper"), hpill("Last 10 weeks", True), hpill("All assets", True)])
            + kpis + row2 + row3 + "</div>")

def page_edge():
    kpis = ('<div class="kpis" style="display:flex;gap:18px;height:138px;flex-shrink:0">'
            + kpi("Expectancy per trade", MINUS + "$13.27", pill("+0.11R", "rgba(78,209,90,.16)", LEAF_L) + " avg R-multiple",
                  [(46, LEAF), (46, RED)], "sigma", dark=True)
            + kpi("Lost past −1R", MINUS + "$8.2K", "40 trades slipped their stop", [(4, RED), (3, RED), (46, RED)], "warn", vcol=RED, badge_bg="#FCE7E5", badge_fg=RED_D)
            + kpi("Won 1R or more", "+$11.6K", "51 trades · the real edge", [(46, LEAF), (34, LEAF), (8, LEAF), (6, LEAF), (4, LEAF)], "trophy", vcol=LEAF, badge_bg="#E3F5E5", badge_fg="#1F7A35")
            + kpi("Stop exits", "80 trades", "0% recovered · " + MINUS + "$12,972", [(46, RED), (10, LEAF), (4, LEAF)], "stop", badge_bg="#FCE7E5", badge_fg=RED_D)
            + '</div>')
    lol = card("Tagged setups earn · untagged legacy bleeds", "Net P&amp;L of the 4 best and 4 worst of 26 strategies · dot size = number of trades",
               f'<div style="margin-top:6px">{lollipop_svg()}</div>', legend='<span style="font-size:11px;color:#6A746C">5 · 20 · 86 trades</span>')
    ladder = ''.join(
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px"><div style="width:80px;font-weight:600;font-size:12px;color:#1F3A26">{n}</div>'
        f'<div style="flex:1;height:12px;border-radius:6px;background:#C3E2C4"><div style="width:{w}%;height:12px;border-radius:6px;background:{LEAF}"></div></div>'
        f'<div style="width:70px;text-align:right;font-weight:700;font-size:12px;color:#1F3A26">{v}</div></div>'
        for n, w, v in [("Market", 100, "+$3,161"), ("Trailing", 90, "+$2,845"), ("Manual", 40, "+$1,258"), ("Take profit", 37, "+$1,163")])
    right = mint_card("+$2,845", LEAF, "from trailing stops · 81% win", ladder + '<div style="display:flex;flex-direction:column;gap:14px;margin-top:10px">'
        + row_icon("target", "Take profit +$1,163", "19 exits · 100% win · avg 1.83R")
        + row_icon("up", "Short MA99 break · 94% win", "18 trades · +1.16R avg · most reliable") + "</div>")
    row2 = f'<div class="row2" style="display:flex;gap:18px;flex:1.2">{lol}{right}</div>'
    dots = card("Every dot is a trade · losses pile up past the stop", "200 trades with a defined stop, grouped by R-multiple (net P&amp;L ÷ planned risk)",
                f'<div style="margin-top:6px">{rdots_svg()}</div>', pill=pill("40 slipped the stop"))
    shorts = dark_card("Shorts carry the book", '<span style="padding:5px 10px;border-radius:10px;background:#FFFFFF;font-weight:600;font-size:11px;color:#0F1712">By side</span>',
        '<div style="display:flex;gap:14px;margin-top:10px">'
        '<div style="flex:1;padding:14px;border-radius:14px;background:rgba(78,209,90,.12)"><div style="font-weight:600;font-size:12px;color:#A6BBAA">Short · 114</div>'
        '<div style="font-weight:800;font-size:26px;letter-spacing:-.02em;color:#4ED15A">+$4,727</div><div style="font-size:11px;color:#A6BBAA">62% win</div></div>'
        '<div style="flex:1;padding:14px;border-radius:14px;background:rgba(224,87,76,.12)"><div style="font-weight:600;font-size:12px;color:#A6BBAA">Long · 241</div>'
        '<div style="font-weight:800;font-size:26px;letter-spacing:-.02em;color:#FF8F85">' + MINUS + '$9,438</div><div style="font-size:11px;color:#A6BBAA">44% win</div></div></div>'
        + units_svg(),
        "68% of trades are long — the losing side")
    row3 = f'<div class="row3" style="display:flex;gap:18px;flex:1">{dots}{shorts}</div>'
    return ("<div class=\"main\">" + header("The Edge", "Where do the wins and losses come from? · R-multiples · exits · strategies",
                                           [hpill("Alpaca · Paper"), hpill("Last 10 weeks", True), hpill("All strategies", True)])
            + kpis + row2 + row3 + "</div>")

def page_desk():
    kpis = ('<div class="kpis" style="display:flex;gap:18px;height:138px;flex-shrink:0">'
            + kpi("Capital deployed", "26%", pill("$24.5K", "rgba(78,209,90,.16)", LEAF_L) + " of $95.8K equity",
                  [(16, LEAF_L), (46, "#3B5A44")], "pie", dark=True, extra_val="")
            + kpi("Unrealized P&amp;L", "+$212", "+0.9% on cost · 4 up, 2 down", [(46, LEAF), (19, RED), (6, LEAF), (6, LEAF), (5, LEAF), (3, RED)], "trend", vcol=LEAF, badge_bg="#E3F5E5", badge_fg=LEAF)
            + kpi("Fill rate", "43.9%", "277 of 631 orders filled", [(39, LEAF), (46, GREY), (3, RED)], "check")
            + kpi("Turnover", "$2.0M", "21× equity in 9 weeks", [(46, LEAF), (45, INK)], "refresh")
            + '</div>')
    tm = card("Open positions · one name carries the gain", "Tile area = market value · colour = return on cost · 6 longs, US equity",
              f'<div style="margin-top:8px">{treemap_svg()}</div>',
              legend='<div style="display:flex;gap:4px;align-items:center"><span style="width:14px;height:10px;border-radius:3px;background:#E0574C"></span><span style="width:14px;height:10px;border-radius:3px;background:#F6CFCA"></span><span style="width:14px;height:10px;border-radius:3px;background:#BDE8C1"></span><span style="width:14px;height:10px;border-radius:3px;background:#2E9E44"></span><span style="font-size:11px;color:#6A746C;margin-left:4px">−2% → +2.5%</span></div>')
    cash = mint_card("$71.3K", INK, '<span style="display:inline-block;width:10px;height:10px;border:2px solid #2E9E44;border-radius:50%"></span> sitting in cash · 74% of equity',
        '<div style="display:flex;flex-direction:column;gap:12px">'
        f'<div style="display:flex;gap:2px;height:14px;border-radius:4px;overflow:hidden;margin-top:12px"><div style="flex:9522;background:#2E9E44"></div><div style="flex:4757;background:#E0574C"></div><div style="flex:3377;background:#7DCB86"></div><div style="flex:2691;background:#7DCB86"></div><div style="flex:2438;background:#7DCB86"></div><div style="flex:1755;background:#F2B5AE"></div><div style="flex:71279;background:#C3E2C4"></div></div>'
        '<div style="display:flex;justify-content:space-between;font-size:11px;color:#4E6553"><span>KO · PANW · DE · MRK · DIS · CRWD</span><span>Cash 74%</span></div>'
        + row_icon("wallet", "Buying power $353,828", "3.7× equity · margin unused")
        + row_icon("pie", "KO is 39% of exposure", "+$235 · more than the whole open gain") + "</div>")
    cash = cash.replace('<div><div style="font-weight:800;font-size:52px', '<div style="position:relative"><div style="position:absolute;right:0;top:0">' + donut() + '</div><div style="font-weight:800;font-size:52px', 1)
    row2 = f'<div class="row2" style="display:flex;gap:18px;flex:1.2">{tm}{cash}</div>'
    sk = card("Where 631 orders went", "Order flow: all orders → side → outcome · band width = order count",
              f'<div style="margin-top:6px">{sankey_svg("52% · mostly bracket legs")}</div>', pill=pill("Cancels are expected", "#E3F5E5", "#1F7A35"))
    cov = dark_card("Market coverage", '<span style="padding:5px 10px;border-radius:10px;background:#FFFFFF;font-weight:600;font-size:11px;color:#0F1712">Daily bars</span>',
        '<div style="display:flex;flex-direction:column;gap:12px;margin-top:8px">'
        '<div style="display:flex;align-items:center;gap:12px"><div style="width:70px;font-weight:600;font-size:12px">Equities</div><div style="flex:1;height:8px;border-radius:4px;background:rgba(255,255,255,.08)"><div style="width:100%;height:8px;border-radius:4px;background:#4ED15A"></div></div><div style="width:50px;text-align:right;font-weight:800;font-size:13px;color:#4ED15A">52/52</div></div>'
        '<div style="display:flex;align-items:center;gap:12px"><div style="width:70px;font-weight:600;font-size:12px">Crypto</div><div style="flex:1;height:8px;border-radius:4px;background:rgba(255,255,255,.08)"><div style="width:53%;height:8px;border-radius:4px;background:#E0574C"></div></div><div style="width:50px;text-align:right;font-weight:800;font-size:13px;color:#FF8F85">16/30</div></div>'
        '<div style="display:flex;flex-wrap:wrap;gap:5px;margin-top:4px">'
        + ''.join(f'<div style="width:50px;text-align:center;padding:3px 0;border-radius:6px;font-size:10px;font-weight:700;color:{c};border:1px solid {b}">{s}</div>'
                  for s, c, b in [(s, "#FF8F85", "rgba(224,87,76,.6)") if s in ("ATOM","BNB","DASH","ENA","INJ","NEAR","OP","SEI","SUI","TAO","WLD","XMR","ZEC","ZEN") else (s, "#4ED15A", "rgba(78,209,90,.3)")
                                  for s in ["AAVE","ADA","ARB","ATOM","AVAX","BNB","BTC","DASH","DOGE","DOT","ENA","ETH","FIL","HYPE","INJ","LINK","LTC","NEAR","OP","PEPE","SEI","SOL","SUI","TAO","UNI","WLD","XMR","XRP","ZEC","ZEN"]])
        + '</div></div>',
        "14 pairs aren't listed on Alpaca. Backfill them from Binance once it's enabled.")
    row3 = f'<div class="row3" style="display:flex;gap:18px;flex:1">{sk}{cov}</div>'
    return ("<div class=\"main\">" + header("The Desk", "What is open right now? · positions · cash · order flow — as of 31 Oct 2026",
                                           [hpill("Alpaca · Paper"), hpill("Today", True), hpill("All assets", True)])
            + kpis + row2 + row3 + "</div>")

CSS_BASE = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#D9DFD9;padding:24px 16px 60px;font-family:'Plus Jakarta Sans',Arial,sans-serif;color:#0F1712}
.wrap{position:relative;width:min(1600px,100%);aspect-ratio:16/9;margin:0 auto 28px;overflow:hidden;background:#EEF2EE;box-shadow:0 1px 4px rgba(0,0,0,.14)}
.board{position:absolute;left:0;top:0;width:1600px;height:900px;display:flex;transform:scale(var(--s,1));transform-origin:0 0;background:#EEF2EE}
.rail{width:80px;flex:none;height:900px;background:linear-gradient(180deg,#0E2215 0%,#081209 100%);display:flex;flex-direction:column;align-items:center;padding:24px 0;gap:36px}
.logo{width:44px;height:44px;border-radius:14px;background:#4ED15A;display:flex;align-items:center;justify-content:center;flex:none}
.nav{width:60px;display:flex;flex-direction:column;align-items:center;gap:6px;padding:10px 0;border-radius:14px}
.main{flex:1;display:flex;flex-direction:column;padding:26px 32px 28px;gap:18px;min-width:0}
.head{height:52px;display:flex;justify-content:space-between;align-items:center;flex:none}
.kpis{display:flex;gap:18px;height:138px;flex:none}
.row2,.row3{display:flex;gap:18px;min-height:0}
.row2{flex:1.2}.row3{flex:1}
.card{border-radius:20px;position:relative;overflow:hidden;min-width:0}
.badge{position:absolute;top:16px;right:18px;width:36px;height:36px;border-radius:12px;display:flex;align-items:center;justify-content:center}
.kpi .badge{position:absolute}
.mint{background:#D9EED9}
svg{display:block}
"""
CSS_GUIDE = """
.board, .board *{font-family:'Barlow',Arial,sans-serif}
.val,.h-title,.card [style*="font-size:52px"],.card [style*="font-size:36px"],.card [style*="font-size:26px"]{font-family:'Anton',Impact,Arial,sans-serif !important;font-weight:400 !important}
.h-title{text-transform:uppercase;letter-spacing:.01em !important}
.head{height:auto !important;padding-top:4px;padding-bottom:6px;gap:16px}.head>div:last-child{white-space:nowrap}
.head div{white-space:nowrap}.head .h-title,.head .guide-kick{white-space:normal}
.main{padding-bottom:70px !important}
.guide-foot{position:absolute;left:112px;right:32px;bottom:14px;display:flex;justify-content:space-between;align-items:flex-end;gap:24px;font-size:16px;color:#4A4A4A}
.guide-foot .note{max-width:1180px;line-height:1.3}
.guide-kick{font-family:'Barlow Condensed',Arial,sans-serif;font-weight:600;font-size:17px;letter-spacing:.08em;color:#666;text-transform:uppercase}
"""

def guide_transform(html, page_no, conclusion, note):
    html = re.sub(r'font-size:(\d+(?:\.\d+)?)px', lambda m: f"font-size:{max(float(m.group(1)), 16):g}px", html)
    html = re.sub(r'font-size="(\d+(?:\.\d+)?)"', lambda m: f'font-size="{max(float(m.group(1)), 16):g}"', html)
    html = html.replace("mostly bracket legs", "296 were sells")
    html = html.replace("Cancels are expected", "296 of 326 cancels were sells")
    html = html.replace("Stops = 54% of gains", "Stops = 54% of gross wins")
    html = html.replace("Is the account growing? · 355 closed trades · 27 Aug – 30 Oct 2026",
                        "355 closed trades · 27 Aug – 30 Oct 2026 · paper account")
    html = re.sub(r'<div class="h-title"[^>]*>([^<]*)</div>',
                  lambda m: f'<div class="guide-kick">{m.group(1)}</div><div class="h-title" style="font-weight:400;font-size:30px;line-height:32px;letter-spacing:.01em;color:{INK};text-transform:uppercase;white-space:normal">{conclusion}</div>', html, count=1)
    foot = (f'<div class="guide-foot"><div class="note">{note}</div>'
            f'<div style="text-align:right;white-space:nowrap">{SRC_LINE}<br><b style="color:#111">{page_no:02d} / 03</b></div></div>')
    return html.replace('</div></div></section>', '</div></div></section>', 0) + foot

SRC_LINE = "Source: gold tables, TradingLakehouse (Trading-Dev) · data to 30 Oct 2026"

PAGES = [
    ("The Book", page_book, "The book is down $4,711, and its losses are bigger than its wins",
     "Daily values are rounded to whole dollars and sum to −$4,705; the exact total is −$4,711. Realized P&amp;L only."),
    ("The Edge", page_edge, "Tagged setups make money. Stops and untagged legacy trades don't.",
     "R-multiples use the planned risk recorded at entry. Strategy labels as recorded in the gold table."),
    ("The Desk", page_desk, "Cash is 74% of equity, and one position carries the open book",
     "Gold orders table: 631 orders vs 639 pulled from Alpaca (8 not matched). 296 of 326 cancels were sell orders."),
]

sections = []
for i, (name, fn, concl, note) in enumerate(PAGES, start=1):
    body = fn()
    if GUIDE:
        # place the conclusion and footer on the page
        body = guide_transform(body, i, concl, note)
    sections.append(frame(rail(name) + body))

css = CSS_BASE + (CSS_GUIDE if GUIDE else "")
title = "The Book · The Edge · The Desk — " + ("guide-final" if GUIDE else "replica")
html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Barlow:wght@400;500;600;700&family=Barlow+Condensed:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Geist+Mono&display=swap" rel="stylesheet">
<style>{css}</style></head>
<body>
{''.join(sections)}
<script>
function fit(){{document.querySelectorAll('.wrap').forEach(w=>w.style.setProperty('--s',w.clientWidth/1600));}}
window.addEventListener('resize',fit);fit();
</script>
</body></html>"""
fname = "dashboard-guide-final.html" if GUIDE else "dashboard-replica.html"
open(f"{OUT_DIR}/{fname}", "w", encoding="utf-8").write(html)
print(fname, len(html))
