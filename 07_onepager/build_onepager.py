from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

pdfmetrics.registerFont(TTFont("DJ","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DJB","/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))

W,H=A4
C=dict(bg="#0a0e1a",panel="#111827",card="#0d1424",border="#2a3548",text="#e5e7eb",
       dim="#94a3b8",mut="#6b7280",gold="#f59e0b",teal="#14b8a6",purple="#8b5cf6",
       pink="#ec4899",red="#ef4444",blue="#3b82f6",green="#10b981")
def col(k): return HexColor(C[k])
c=canvas.Canvas("Titan_Investor_OnePager.pdf",pagesize=A4)

def rrect(x,y,w,h,fill=None,stroke=None,r=8,lw=0.7):
    if fill: c.setFillColor(fill if isinstance(fill,Color) else col(fill))
    if stroke: c.setStrokeColor(stroke if isinstance(stroke,Color) else col(stroke)); c.setLineWidth(lw)
    c.roundRect(x,y,w,h,r,stroke=1 if stroke else 0,fill=1 if fill else 0)
def T(x,y,s,f="DJ",sz=9,k="text",align="l"):
    c.setFont(f,sz); c.setFillColor(col(k))
    if align=="c": c.drawCentredString(x,y,s)
    elif align=="r": c.drawRightString(x,y,s)
    else: c.drawString(x,y,s)
def wrap(s,f,sz,maxw):
    words=s.split(); lines=[]; cur=""
    for w_ in words:
        t=(cur+" "+w_).strip()
        if pdfmetrics.stringWidth(t,f,sz)<=maxw: cur=t
        else: lines.append(cur); cur=w_
    if cur: lines.append(cur)
    return lines
def para(x,y,s,f="DJ",sz=8,k="dim",maxw=250,lead=11):
    for ln in wrap(s,f,sz,maxw): T(x,y,ln,f,sz,k); y-=lead
    return y

# page bg
c.setFillColor(col("bg")); c.rect(0,0,W,H,fill=1,stroke=0)
M=26; CW=W-2*M; top=H-24

# ---------- HEADER ----------
T(M,top-6,"TITAN COMPANY LTD","DJB",18,"text")
T(M,top-22,"NSE: TITAN   ·   Independent Equity Research   ·   FY25-reanchored DCF","DJ",8.5,"dim")
# HOLD badge
bw,bh=66,22; bx=W-M-bw; by=top-20
rrect(bx,by,bw,bh,fill=HexColor("#3a2a08"),stroke="gold",r=6,lw=1)
T(bx+bw/2,by+7,"HOLD","DJB",11,"gold",align="c")
T(W-M,top-30,"Shivang Koul · June 2026","DJ",7.5,"mut",align="r")
y=top-46

# ---------- KPI STRIP ----------
kpis=[("Current price","₹4,363","text"),("DCF fair value","₹1,017","teal"),
      ("Downside","−77%","red"),("Implied perpetual growth","11.3%","gold"),
      ("WACC","12.2%","text")]
n=len(kpis); gap=8; kw=(CW-(n-1)*gap)/n; kh=44; ky=y-kh
for i,(lab,val,kc) in enumerate(kpis):
    kx=M+i*(kw+gap); rrect(kx,ky,kw,kh,fill="card",stroke="border",r=7)
    T(kx+10,ky+kh-15,lab,"DJ",7.5,"dim")
    T(kx+10,ky+10,val,"DJB",16,kc)
y=ky-12

# ---------- THESIS ----------
thesis=("Titan is a best-in-class compounder — the dominant organised jewellery franchise (Tanishq), a long "
"formalisation runway and excellent execution. But quality is not the question here; price is. At ~₹4,363 the stock "
"trades at roughly 90–97× earnings, while a two-stage DCF anchored to FY25 audited actuals yields a fair value of "
"₹1,017 — about 77% below the market. A reverse-DCF shows the price already embeds ~11.3% perpetual FCFF growth "
"versus ~5.5% nominal GDP. A superb business with no margin of safety. Recommendation: HOLD.")
th=58; ty=y-th
rrect(M,ty,CW,th,fill="panel",stroke="border",r=8)
T(M+12,ty+th-15,"THESIS","DJB",8.5,"gold")
para(M+12,ty+th-30,thesis,"DJ",8.6,"text",maxw=CW-24,lead=11.2)
y=ty-12

# ---------- 2x2 GRID ----------
panels=[
 ("◆ Valuation · DCF","teal","figs/valuation.png",
  "Two-stage 10-yr FCFF · WACC 12.2% (Rf 7.0, ERP 6.5, β 0.85) · TV 65% of EV. Fair value ₹1,017; EV ₹1,01,522 Cr. Reverse-DCF: the market implies ~11.3% perpetual growth to justify today's price."),
 ("◆ Monte Carlo · 10,000 trials","purple","figs/montecarlo.png",
  "Median ₹1,005, 80% CI ₹718–₹1,387. P(fair value < CMP) = 100% — not one simulated path reaches ₹4,363. Largest swing factors: EBITDA margin (+0.61) and WACC (−0.56)."),
 ("◆ Management sentiment · LLM","pink","figs/sentiment.png",
  "6 real earnings calls scored across 5 analyst dimensions. Confidence is mildly positive and stable (MCI +0.10) — strong growth conviction, tempered by margin caution and hedging. Bounded overlay moves FV only ₹1,013→₹1,018."),
 ("◆ Alt-data · Google Trends","gold","figs/trends.png",
  "'Tanishq' search vs jewellery revenue. Raw levels look predictive, but detrended the signal is coincident, not leading — lag +1 r = −0.10 (ns). An honestly-reported null, not manufactured alpha."),
]
pw=(CW-12)/2; ph=176
imgw=pw-20
for idx,(head,acc,img,cap) in enumerate(panels):
    r_,cc=divmod(idx,2)
    px=M+cc*(pw+12); py=y-(r_+1)*ph-(r_*12)
    rrect(px,py,pw,ph,fill="panel",stroke="border",r=8)
    T(px+12,py+ph-16,head,"DJB",9.5,acc)
    ir=ImageReader(img); iw,ih=ir.getSize(); dh=imgw*ih/iw
    c.drawImage(ir,px+10,py+ph-24-dh,width=imgw,height=dh,mask='auto')
    cy=py+ph-30-dh
    para(px+12,cy,cap,"DJ",7.6,"dim",maxw=pw-24,lead=9.6)
y=y-2*ph-12-12

# ---------- FOOTER ----------
fh=120; fy=y-fh
rrect(M,fy,CW,fh,fill="card",stroke="border",r=8)
yy=fy+fh-15
T(M+12,yy,"WHAT WOULD CHANGE THE VIEW","DJB",8,"teal"); yy-=12
yy=para(M+12,yy,"A durable step-up in the growth algorithm (mid-to-high teens for longer) or structural margin expansion beyond ~11.5% would narrow the gap — but justifying ₹4,363 still requires underwriting ~11% perpetual FCFF growth, well above nominal GDP.","DJ",7.6,"dim",maxw=CW-24,lead=9.6)-3
T(M+12,yy,"METHODOLOGY & DATA INTEGRITY","DJB",8,"gold"); yy-=12
yy=para(M+12,yy,"FY25-reanchored 3-statement model balances every year FY21–34; bullion ex-revenue; full Ind-AS 116 leases; jewellery on a standalone ex-bullion basis that reconciles 0.00% to Titan's filings. Conclusion reached by analysis — never reverse-engineered to market price — and cross-checked with an independent Python recompute.","DJ",7.6,"dim",maxw=CW-24,lead=9.6)-2
T(M+12,yy,"Sources: Titan FY25 audited filings & 6 earnings-call transcripts · Monte Carlo (n=10,000) · Google Trends (live). Independent research — not investment advice.","DJ",7,"mut")

c.showPage(); c.save()
print("PDF built")
