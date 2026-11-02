import datetime as dt, math, os
OUT=os.path.join(os.path.dirname(__file__),'svg')
F='font-family="Plus Jakarta Sans"'
def w(n,s): open(os.path.join(OUT,n),'w').write(s)
# daily DD for mint card p1
raw=open(os.path.join(os.path.dirname(__file__),'gen.py')).read().split('raw="""')[1].split('"""')[0]
pts=[(dt.date.fromisoformat(a),int(b)) for a,b in (x.split(',') for x in raw.split())]
d0=dt.date(2026,8,26);d1=dt.date(2026,10,31);span=(d1-d0).days
W,H=420,78;X=lambda d:(d-d0).days/span*W
cum=0;pk=0;dd=[(d0,0)]
for d,v in pts: cum+=v;pk=max(pk,cum);dd.append((d,cum-pk))
Y=lambda v:8+(-v)/10000*(H-26)
line=" ".join(f"{'M' if i==0 else 'L'}{X(d):.1f} {Y(v):.1f}" for i,(d,v) in enumerate(dd))
area=line+f" L{X(dd[-1][0]):.1f} 8 L0 8 Z"
lo=min(dd,key=lambda r:r[1])
s=f'''<svg layer-name="Mini · Drawdown" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" style="flex-shrink:0">
<line x1="0" y1="8" x2="{W}" y2="8" stroke="#9CC9A0"/>
<path d="{area}" fill="#E0574C" fill-opacity="0.16"/><path d="{line}" stroke="#E0574C" stroke-width="1.8" stroke-linejoin="round"/>
<circle cx="{X(lo[0]):.1f}" cy="{Y(lo[1]):.1f}" r="4" fill="#E0574C" stroke="#D9EED9" stroke-width="2"/>
<text x="{X(lo[0])+8:.1f}" y="{Y(lo[1])+4:.1f}" {F} font-size="10" font-weight="700" fill="#B5352B">17 Sep</text>
<text x="0" y="{H-2}" {F} font-size="10" fill="#4E6553">27 Aug</text><text x="{W}" y="{H-2}" {F} font-size="10" fill="#4E6553" text-anchor="end">30 Oct · −$7.6K below peak</text>
</svg>'''
w('m1_dd.svg',s)

# dark p1: crypto vs equity cumulative weekly
c=[0,-555,-475,180,591,784,-383,445,-219,262];e=[2871,-793,-4556,-1756,2041,6,-1210,435,326,266]
cc=[];ce=[];a=b=0
for x,y in zip(c,e): a+=x;b+=y;cc.append(a);ce.append(b)
W,H=430,72;lo_,hi_=-4800,3200
Y=lambda v:6+(hi_-v)/(hi_-lo_)*(H-14)
X=lambda i:i*(W-70)/9
def pl(arr): return " ".join(f"{'M' if i==0 else 'L'}{X(i):.1f} {Y(v):.1f}" for i,v in enumerate(arr))
s=f'''<svg layer-name="Mini · Crypto vs Equity" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" style="flex-shrink:0">
<line x1="0" y1="{Y(0):.1f}" x2="{W-70}" y2="{Y(0):.1f}" stroke="rgba(255,255,255,0.18)" stroke-dasharray="3 3"/>
<path d="{pl(ce)}" stroke="#E0574C" stroke-width="2" stroke-linejoin="round"/>
<path d="{pl(cc)}" stroke="#4ED15A" stroke-width="2.4" stroke-linejoin="round"/>
<circle cx="{X(9):.1f}" cy="{Y(cc[-1]):.1f}" r="4" fill="#4ED15A"/><circle cx="{X(9):.1f}" cy="{Y(ce[-1]):.1f}" r="4" fill="#E0574C"/>
<text x="{X(9)+10:.1f}" y="{Y(cc[-1])+4:.1f}" {F} font-size="11" font-weight="700" fill="#4ED15A">Crypto</text>
<text x="{X(9)+10:.1f}" y="{Y(ce[-1])+4:.1f}" {F} font-size="11" font-weight="700" fill="#FF8F85">Equity</text>
</svg>'''
w('d1_lines.svg',s)

# mint p2: exit ladder
ex=[("Market",3161),("Trailing",2845),("Manual",1258),("Take profit",1163)]
W,H=420,78;out=[]
for i,(n,v) in enumerate(ex):
    y=i*19.5;bw=v/3161*(W-170)
    out.append(f'<text x="0" y="{y+13}" {F} font-size="12" font-weight="600" fill="#1F3A26">{n}</text><rect x="90" y="{y+3}" width="{W-170}" height="12" rx="6" fill="#C3E2C4"/><rect x="90" y="{y+3}" width="{bw:.1f}" height="12" rx="6" fill="#2E9E44"/><text x="{W}" y="{y+13}" {F} font-size="12" font-weight="700" fill="#1F3A26" text-anchor="end">+${v:,}</text>')
w('m2_exits.svg',f'<svg layer-name="Mini · Profitable Exits" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" style="flex-shrink:0">'+''.join(out)+'</svg>')

# dark p2: win/loss split per side as unit squares (1 square = 5 trades)
W,H=430,74
rows=[("Short",71,43),("Long",107,134)]
out=[]
for r,(n,wn,ls) in enumerate(rows):
    y=r*38;x=58
    out.append(f'<text x="0" y="{y+14}" {F} font-size="12" font-weight="600" fill="#DDE9DF">{n}</text>')
    for k in range(round(wn/5)): out.append(f'<rect x="{x:.1f}" y="{y+3}" width="6" height="14" rx="1.5" fill="#4ED15A"/>');x+=7.4
    x+=4
    for k in range(round(ls/5)): out.append(f'<rect x="{x:.1f}" y="{y+3}" width="6" height="14" rx="1.5" fill="#E0574C"/>');x+=7.4
    out.append(f'<text x="58" y="{y+32}" {F} font-size="10" fill="#8FA594">{wn} won · {ls} lost</text>')
w('d2_units.svg',f'<svg layer-name="Mini · Win Loss Units" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" style="flex-shrink:0">'+''.join(out)+'</svg>')

# mint p3: donut cash vs invested
r=44;C=2*math.pi*r;inv=24540/95819
s=f'''<svg layer-name="Mini · Cash Donut" width="112" height="112" viewBox="0 0 112 112" fill="none" style="flex-shrink:0">
<circle cx="56" cy="56" r="{r}" stroke="#C3E2C4" stroke-width="14"/>
<circle cx="56" cy="56" r="{r}" stroke="#2E9E44" stroke-width="14" stroke-dasharray="{C*inv:.1f} {C:.1f}" stroke-linecap="round" transform="rotate(-90 56 56)"/>
<text x="56" y="56" {F} font-size="18" font-weight="800" fill="#0F1712" text-anchor="middle">26%</text>
<text x="56" y="71" {F} font-size="9" font-weight="600" fill="#4E6553" text-anchor="middle">INVESTED</text>
</svg>'''
w('m3_donut.svg',s)
print('ok')
