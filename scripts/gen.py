import datetime as dt, math, os
OUT=os.path.join(os.path.dirname(__file__),'svg')
F='font-family="Plus Jakarta Sans"'
LEAF='#4ED15A';LEAF6='#2E9E44';LEAF3='#A9E5AE';INK='#0F1712';MUT='#6A746C';HAIR='#E3E8E3';LOSS='#E0574C';LOSS3='#F2B5AE'
def w(name,s): open(os.path.join(OUT,name),'w').write(s)

# ---------- P1A equity curve + underwater ----------
raw="""2026-08-27,2871 2026-08-31,-741 2026-09-01,-114 2026-09-02,-92 2026-09-03,-156 2026-09-04,-69 2026-09-05,-579 2026-09-06,64 2026-09-07,-20 2026-09-08,-2161 2026-09-09,-1146 2026-09-10,-954 2026-09-11,-1172 2026-09-13,14 2026-09-14,143 2026-09-15,-1760 2026-09-16,-28 2026-09-17,-1060 2026-09-18,31 2026-09-19,96 2026-09-20,-93 2026-09-21,-20 2026-09-22,1950 2026-09-23,222 2026-09-24,-14 2026-09-25,504 2026-09-26,85 2026-09-28,-221 2026-09-29,-44 2026-09-30,-231 2026-10-01,-204 2026-10-02,213 2026-10-03,145 2026-10-04,77 2026-10-05,10 2026-10-06,-168 2026-10-07,-1477 2026-10-08,-197 2026-10-09,169 2026-10-11,-94 2026-10-12,-19 2026-10-13,2085 2026-10-14,-402 2026-10-15,-324 2026-10-16,-931 2026-10-17,468 2026-10-18,5 2026-10-19,202 2026-10-20,-243 2026-10-21,-131 2026-10-22,-575 2026-10-23,568 2026-10-24,286 2026-10-26,355 2026-10-27,57 2026-10-28,-546 2026-10-29,665 2026-10-30,-4"""
pts=[(dt.date.fromisoformat(a),int(b)) for a,b in (x.split(',') for x in raw.split())]
d0=dt.date(2026,8,26);d1=dt.date(2026,10,31);span=(d1-d0).days
W,H=900,214;L,R=44,8
X=lambda d: L+(d-d0).days/span*(W-L-R)
cum=0;peak=0;rows=[(d0,0,0)]
for d,v in pts:
    cum+=v;peak=max(peak,cum);rows.append((d,cum,cum-peak))
lo,hi=-8000,4000;T0,T1=8,128
Y=lambda v: T1-(v-lo)/(hi-lo)*(T1-T0)
U0,U1=146,188;dmin=-10000
UY=lambda v: U0+(v/dmin)*(U1-U0)
line=" ".join(f"{'M' if i==0 else 'L'}{X(d):.1f} {Y(c):.1f}" for i,(d,c,_) in enumerate(rows))
area=line+f" L{X(rows[-1][0]):.1f} {Y(0):.1f} L{X(d0):.1f} {Y(0):.1f} Z"
uw="".join(f"L{X(d):.1f} {UY(dd):.1f} " for d,_,dd in rows)
uw=f"M{X(d0):.1f} {U0} "+uw+f"L{X(rows[-1][0]):.1f} {U0} Z"
mi=min(rows,key=lambda r:r[1]);md=min(rows,key=lambda r:r[2])
g=[]
for v,lab in [(4000,'+$4K'),(0,'$0'),(-4000,'−$4K'),(-8000,'−$8K')]:
    g.append(f'<line x1="{L}" y1="{Y(v):.1f}" x2="{W-R}" y2="{Y(v):.1f}" stroke="{HAIR if v else "#BFC8C0"}"/><text x="0" y="{Y(v)+4:.1f}" {F} font-size="10" fill="{MUT}">{lab}</text>')
ticks="".join(f'<text x="{X(dt.date.fromisoformat(s)):.1f}" y="210" {F} font-size="10" fill="{MUT}" text-anchor="middle">{t}</text>' for s,t in [("2026-09-01","1 Sep"),("2026-09-15","15 Sep"),("2026-10-01","1 Oct"),("2026-10-15","15 Oct"),("2026-10-29","29 Oct")])
px,py=X(rows[1][0]),Y(rows[1][1]);tx,ty=X(mi[0]),Y(mi[1]);ex,ey=X(rows[-1][0]),Y(rows[-1][1]);ux,uy=X(md[0]),UY(md[2])
s=f'''<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none">
<defs><linearGradient id="ga" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{LEAF}" stop-opacity="0.28"/><stop offset="1" stop-color="{LEAF}" stop-opacity="0"/></linearGradient></defs>
{''.join(g)}
<path d="{area}" fill="url(#ga)"/>
<path d="{line}" stroke="{LEAF6}" stroke-width="2" stroke-linejoin="round"/>
<text x="0" y="{U0+12}" {F} font-size="10" fill="{MUT}">DD</text>
<line x1="{L}" y1="{U0}" x2="{W-R}" y2="{U0}" stroke="#BFC8C0"/>
<path d="{uw}" fill="{LOSS}" fill-opacity="0.22" stroke="{LOSS}" stroke-width="1.2"/>
<circle cx="{px:.1f}" cy="{py:.1f}" r="4.5" fill="#fff" stroke="{LEAF6}" stroke-width="2"/>
<rect x="{px+10:.1f}" y="{py-11:.1f}" width="94" height="22" rx="11" fill="{INK}"/><text x="{px+57:.1f}" y="{py+4:.1f}" {F} font-size="11" font-weight="600" fill="{LEAF}" text-anchor="middle">Peak +$2,871</text>
<circle cx="{tx:.1f}" cy="{ty:.1f}" r="4.5" fill="#fff" stroke="{LOSS}" stroke-width="2"/>
<rect x="{tx-50:.1f}" y="{ty+9:.1f}" width="100" height="22" rx="11" fill="{INK}"/><text x="{tx:.1f}" y="{ty+24:.1f}" {F} font-size="11" font-weight="600" fill="#FFB1A9" text-anchor="middle">Low {('−$'+format(-mi[1],','))}</text>
<circle cx="{ex:.1f}" cy="{ey:.1f}" r="5" fill="{LEAF6}"/>
<text x="{ex-8:.1f}" y="{ey-10:.1f}" {F} font-size="12" font-weight="700" fill="{INK}" text-anchor="end">−$4,711</text>
<text x="{ux+8:.1f}" y="{uy+4:.1f}" {F} font-size="10" font-weight="600" fill="{LOSS}">Max drawdown {('−$'+format(-md[2],','))}</text>
{ticks}
</svg>'''
w('p1a_equity.svg',s); print('p1a low',mi,'maxdd',md)

# ---------- P1B horizontal waterfall ----------
W,H=900,150;LX=170;RX=W-90
vmin,vmax=-6000,24000
SX=lambda v: LX+(v-vmin)/(vmax-vmin)*(RX-LX)
steps=[("Gross wins",0,23859,LEAF6,"+$23,859"),("Stop exits",23859,10887,LOSS,"−$12,972"),("Other losses",10887,-4711,LOSS3,"−$15,598"),("Net P&L",0,-4711,INK,"−$4,711")]
out=[f'<line x1="{SX(0):.1f}" y1="0" x2="{SX(0):.1f}" y2="{H-14}" stroke="#BFC8C0"/>']
rh=22;gap=12
for i,(lab,a,b,c,val) in enumerate(steps):
    y=4+i*(rh+gap);x0,x1=sorted([SX(a),SX(b)])
    out.append(f'<text x="0" y="{y+15}" {F} font-size="13" font-weight="{700 if i==3 else 500}" fill="{INK}">{lab}</text>')
    out.append(f'<rect x="{x0:.1f}" y="{y}" width="{x1-x0:.1f}" height="{rh}" rx="6" fill="{c}"/>')
    out.append(f'<text x="{W}" y="{y+15}" {F} font-size="13" font-weight="700" fill="{LEAF6 if val.startswith("+") else (INK if i==3 else LOSS)}" text-anchor="end">{val}</text>')
    if i<3:
        nx=SX(b);out.append(f'<line x1="{nx:.1f}" y1="{y+rh}" x2="{nx:.1f}" y2="{y+rh+gap}" stroke="{MUT}" stroke-dasharray="2 2"/>')
for v,t in [(0,'$0'),(10000,'$10K'),(20000,'$20K')]:
    out.append(f'<text x="{SX(v):.1f}" y="{H-2}" {F} font-size="10" fill="{MUT}" text-anchor="middle">{t}</text>')
w('p1b_waterfall.svg',f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none">'+''.join(out)+'</svg>')

# ---------- P2A diverging lollipop ----------
strats=[("equity-one-dissent-half",1282,19),("equity-hourly-close-xc1",1232,5),("short-ma99-break",806,18),("long-pullback",438,86),("option-debit-spread",-973,12),("equity-legacy-untagged",-1679,22),("equity-swing-long",-1864,11),("option-legacy-untagged",-2000,19)]
W,H=900,214;LX=232;RX=W-70;Z=LX+(RX-LX)*2200/3700
SX=lambda v: Z+v/3700*(RX-LX)
out=[f'<line x1="{Z:.1f}" y1="0" x2="{Z:.1f}" y2="{H-16}" stroke="#BFC8C0"/>']
for v,t in [(-2000,'−$2K'),(-1000,'−$1K'),(0,'$0'),(1000,'+$1K')]:
    out.append(f'<text x="{SX(v):.1f}" y="{H-2}" {F} font-size="10" fill="{MUT}" text-anchor="middle">{t}</text>')
    if v: out.append(f'<line x1="{SX(v):.1f}" y1="0" x2="{SX(v):.1f}" y2="{H-16}" stroke="{HAIR}" stroke-dasharray="2 3"/>')
for i,(n,v,c) in enumerate(strats):
    y=12+i*24.5;col=LEAF6 if v>0 else LOSS;x=SX(v);r=3.5+math.sqrt(c)*0.95
    out.append(f'<text x="0" y="{y+4}" font-family="Geist Mono" font-size="12" fill="{INK}">{n}</text>')
    out.append(f'<line x1="{Z:.1f}" y1="{y}" x2="{x:.1f}" y2="{y}" stroke="{col}" stroke-width="2"/>')
    out.append(f'<circle cx="{x:.1f}" cy="{y}" r="{r:.1f}" fill="{col}" fill-opacity="0.9" stroke="#fff" stroke-width="1.5"/>')
    lx=x+r+6 if v>0 else x-r-6
    out.append(f'<text x="{lx:.1f}" y="{y+4}" {F} font-size="12" font-weight="700" fill="{col}" text-anchor="{"start" if v>0 else "end"}">{"+" if v>0 else "−"}${abs(v):,}</text>')
    out.append(f'<text x="{W}" y="{y+4}" {F} font-size="11" fill="{MUT}" text-anchor="end">{c} trades</text>')
out.insert(0,f'<rect x="{LX-8}" y="{12+3.5*24.5:.1f}" width="{W-LX+8}" height="1" fill="{HAIR}"/>')
w('p2a_lollipop.svg',f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none">'+''.join(out)+'</svg>')

# ---------- P2B dot matrix histogram ----------
bins=[("−2.5",2),("−2",1),("−1.5",37),("−1",44),("−0.5",11),("0",33),("+0.5",21),("+1",24),("+1.5",18),("+2",4),("+2.5",3),("+3",2)]
W,H=900,150;PER=4;SP=9.2;R0=3.4;base=124;colw=W/12
out=[f'<line x1="0" y1="{base+6}" x2="{W}" y2="{base+6}" stroke="#BFC8C0"/>']
for i,(lab,n) in enumerate(bins):
    c=LOSS if i<=2 else (LOSS3 if i<=4 else (LEAF3 if i<=6 else LEAF6))
    cx=i*colw+colw/2-(PER-1)*SP/2
    for k in range(n):
        r,cc=divmod(k,PER)
        out.append(f'<circle cx="{cx+cc*SP:.1f}" cy="{base-r*SP:.1f}" r="{R0}" fill="{c}"/>')
    out.append(f'<text x="{i*colw+colw/2:.1f}" y="{H-2}" {F} font-size="11" fill="{MUT}" text-anchor="middle">{lab}R</text>')
    if n>=20: out.append(f'<text x="{i*colw+colw/2:.1f}" y="{base-math.ceil(n/PER)*SP-2:.1f}" {F} font-size="11" font-weight="700" fill="{INK}" text-anchor="middle">{n}</text>')
sx=3*colw
out.append(f'<line x1="{sx:.1f}" y1="0" x2="{sx:.1f}" y2="{base+6}" stroke="{INK}" stroke-dasharray="3 3"/><text x="{sx-6:.1f}" y="10" {F} font-size="10" font-weight="700" fill="{INK}" text-anchor="end">PLANNED STOP</text>')
bx=5*colw
out.append(f'<line x1="{bx:.1f}" y1="0" x2="{bx:.1f}" y2="{base+6}" stroke="#BFC8C0"/><text x="{bx+6:.1f}" y="10" {F} font-size="10" font-weight="600" fill="{MUT}">BREAK-EVEN</text>')
w('p2b_dots.svg',f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none">'+''.join(out)+'</svg>')

# ---------- P3A treemap (squarified) ----------
pos=[("KO",9522,235,2.53,1.57),("PANW",4757,-97,-1.99,-3.85),("DE",3377,27,0.80,2.34),("MRK",2691,29,1.10,2.16),("DIS",2438,24,0.97,-0.10),("CRWD",1755,-7,-0.39,-3.97)]
W,H=900,214
def worst(row,wd):
    s=sum(row);return max(max(wd*wd*r/(s*s),s*s/(wd*wd*r)) for r in row)
def squarify(vals,x,y,w_,h_):
    out=[];vals=list(vals)
    while vals:
        wd=min(w_,h_);row=[vals[0]]
        i=1
        while i<len(vals) and worst(row+[vals[i]],wd)<=worst(row,wd): row.append(vals[i]);i+=1
        s=sum(row)
        if w_>=h_:
            cw=s/h_;cy=y
            for r in row: out.append((x,cy,cw,r/cw));cy+=r/cw
            x+=cw;w_-=cw
        else:
            ch=s/w_;cx=x
            for r in row: out.append((cx,y,r/ch,ch));cx+=r/ch
            y+=ch;h_-=ch
        vals=vals[len(row):]
    return out
tot=sum(p[1] for p in pos);areas=[p[1]/tot*W*H for p in pos]
rects=squarify(areas,0,0,W,H)
def col(ret):
    if ret>=2: return LEAF6,'#FFFFFF','#D7F5DA'
    if ret>=0: return '#BDE8C1',INK,'#2E6B3A'
    if ret>-1: return '#F6CFCA',INK,'#9A2E25'
    return LOSS,'#FFFFFF','#FFE1DD'
out=[]
for (x,y,ww,hh),(sym,mv,pl,ret,tod) in zip(rects,pos):
    bg,fg,sub=col(ret);g=3
    out.append(f'<rect x="{x+g/2:.1f}" y="{y+g/2:.1f}" width="{ww-g:.1f}" height="{hh-g:.1f}" rx="10" fill="{bg}"/>')
    big=ww>200
    out.append(f'<text x="{x+14:.1f}" y="{y+(30 if big else 24):.1f}" font-family="Geist Mono" font-size="{20 if big else 14}" font-weight="600" fill="{fg}">{sym}</text>')
    out.append(f'<text x="{x+14:.1f}" y="{y+(52 if big else 42):.1f}" {F} font-size="{13 if big else 11}" fill="{sub}">${mv:,} · {mv/tot*100:.0f}%</text>')
    out.append(f'<text x="{x+ww-12:.1f}" y="{y+hh-12:.1f}" {F} font-size="{22 if big else 13}" font-weight="800" fill="{fg}" text-anchor="end">{"+" if ret>=0 else "−"}{abs(ret):.2f}%</text>')
w('p3a_treemap.svg',f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none">'+''.join(out)+'</svg>')
print('treemap',[tuple(round(v) for v in r) for r in rects])

# ---------- P3B sankey ----------
W,H=900,150;k=(H-2-3*6)/631;NW=10
L1=[("631 orders",631)];L2=[("Buy",141),("Sell",459),("Other",31)];L3=[("Filled",277),("Canceled",326),("Expired",15),("Working",13)]
X1,X2,X3=110,420,720
def stack(nodes,gap=6):
    y=1;r={}
    for n,v in nodes: r[n]=[y,y+v*k];y+=v*k+gap
    return r
n1,n2,n3=stack(L1),stack(L2),stack(L3)
f12=[("631 orders","Buy",141),("631 orders","Sell",459),("631 orders","Other",31)]
f23=[("Buy","Filled",116),("Buy","Canceled",23),("Buy","Expired",2),("Sell","Filled",145),("Sell","Canceled",296),("Sell","Expired",6),("Sell","Working",12),("Other","Filled",16),("Other","Canceled",7),("Other","Expired",7),("Other","Working",1)]
SC={"Filled":LEAF6,"Canceled":"#9AA59C","Expired":LOSS,"Working":"#C9D2CA"}
out=[]
def band(xa,ya,xb,yb,h,color,op):
    m=(xa+xb)/2
    return f'<path d="M{xa} {ya:.2f} C{m} {ya:.2f} {m} {yb:.2f} {xb} {yb:.2f} L{xb} {yb+h:.2f} C{m} {yb+h:.2f} {m} {ya+h:.2f} {xa} {ya+h:.2f} Z" fill="{color}" fill-opacity="{op}"/>'
oa={n:v[0] for n,v in n1.items()};ia={n:v[0] for n,v in n2.items()}
for a,b,v in f12:
    h=v*k;out.append(band(X1+NW,oa[a],X2,ia[b],h,"#7FA488",0.35));oa[a]+=h;ia[b]+=h
oa={n:v[0] for n,v in n2.items()};ia={n:v[0] for n,v in n3.items()}
for a,b,v in f23:
    h=v*k;out.append(band(X2+NW,oa[a],X3,ia[b],h,SC[b],0.45));oa[a]+=h;ia[b]+=h
for nodes,x,colr in [(n1,X1,INK),(n2,X2,INK)]:
    for n,(a,b) in nodes.items(): out.append(f'<rect x="{x}" y="{a:.1f}" width="{NW}" height="{max(b-a,2):.1f}" rx="2" fill="{colr}"/>')
for n,(a,b) in n3.items(): out.append(f'<rect x="{X3}" y="{a:.1f}" width="{NW}" height="{max(b-a,2):.1f}" rx="2" fill="{SC[n]}"/>')
m=(n1["631 orders"][0]+n1["631 orders"][1])/2
out.append(f'<text x="{X1-10}" y="{m-4:.1f}" {F} font-size="22" font-weight="800" fill="{INK}" text-anchor="end">631</text><text x="{X1-10}" y="{m+14:.1f}" {F} font-size="11" fill="{MUT}" text-anchor="end">orders</text>')
for n,(a,b) in n2.items():
    v=dict(L2)[n];out.append(f'<text x="{X2-8}" y="{(a+b)/2+4:.1f}" {F} font-size="12" font-weight="600" fill="{INK}" text-anchor="end">{n} {v}</text>')
for n,(a,b) in n3.items():
    v=dict(L3)[n];yy=(a+b)/2+4
    if n=="Expired": yy=a-1
    if n=="Working": yy=b+11
    out.append(f'<text x="{X3+NW+10}" y="{yy:.1f}" {F} font-size="12" font-weight="700" fill="{SC[n] if n!="Working" else MUT}">{n} <tspan fill="{INK}">{v}</tspan> <tspan font-weight="400" fill="{MUT}">· {v/631*100:.0f}%</tspan></text>')
w('p3b_sankey.svg',f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none">'+''.join(out)+'</svg>')
print('done')
