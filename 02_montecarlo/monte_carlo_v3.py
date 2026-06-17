"""
TITAN — Monte Carlo DCF v3 (reanchored to FY25 actuals)
Wraps the VERIFIED two-stage DCF engine (central case = Rs 1,013, matches the
deterministic model's Rs 1,017) in input distributions. 10,000 simulations.
Key corrections vs old v2: FY25 base (not FY24), two-stage 10-yr (not flat 5-yr),
WACC centered 12.2% (not 9.5%), EBITDA margin centered 11.4% (not 12.7%),
NWC net of gold-on-loan, CMP 4,363.
"""
import numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
np.random.seed(42); N=10_000

# ---- VERIFIED ANCHORS (reanchored model, FY25 audited) ----
CORE_FY25=57332.0
INV_FY25,REC_FY25,PAY_FY25,OCL_FY25,GOLD_FY25=28184.,1068.,1963.,4441.,7810.
NETDEBT=11223.0; SHARES=88.8; CMP=4363.0
NWC0=INV_FY25+REC_FY25-PAY_FY25-OCL_FY25-GOLD_FY25   # FY25 net WC base

# fixed structure (two-stage fade); FY26 ~ Damas-inflated (near-known)
g_base=np.array([0.306,0.16,0.14,0.125,0.115,0.10,0.085,0.07,0.055])  # FY26..FY34
invd_base=np.array([165,163,161,159,157,156,155,154,153.])
RECD,PAYD,OCLP,GOLDP=7.,12.,0.08,0.28

# ---- DISTRIBUTIONS ----
# growth: parallel shift on the high-growth phase FY27-FY30 (FY26 ~known, fade fixed)
g_shift   = np.random.normal(0.00, 0.025, N).clip(-0.06, 0.06)
margin    = np.random.normal(0.114, 0.012, N).clip(0.085, 0.140)   # steady EBITDA margin on core
wacc      = np.random.normal(0.122, 0.008, N).clip(0.100, 0.145)
tgr       = np.random.normal(0.055, 0.007, N).clip(0.035, 0.075)
tax       = np.random.normal(0.255, 0.010, N).clip(0.22, 0.29)
da_pct    = np.random.normal(0.012, 0.002, N).clip(0.007, 0.018)
capex_pct = np.random.normal(0.013, 0.003, N).clip(0.007, 0.022)
invd_shift= np.random.normal(0.0, 8.0, N).clip(-25, 25)   # inventory-days (gold-price sensitivity)

prices=np.full(N,np.nan)
for k in range(N):
    g=g_base.copy()
    g[1:5]=g[1:5]+g_shift[k]              # shift FY27-FY30
    g=g.clip(0.0,0.6)
    # margin path: ramp FY26/27 below steady, then steady = margin[k]
    m=np.full(9, margin[k]); m[0]=margin[k]-0.005; m[1]=margin[k]-0.003
    invd=(invd_base+invd_shift[k]).clip(120,210)
    core=CORE_FY25; prev=core; nwc_prev=NWC0; sumpv=0.0; fcff_last=0.0
    for t in range(9):
        core=prev*(1+g[t])
        ebit=core*m[t]-core*da_pct[k]
        nopat=ebit*(1-tax[k])
        inv=core/365*invd[t]; rec=core/365*RECD; pay=core/365*PAYD
        ocl=core*OCLP; gold=inv*GOLDP
        nwc=inv+rec-pay-ocl-gold; dnwc=nwc-nwc_prev
        fcff=nopat+core*da_pct[k]-core*capex_pct[k]-dnwc
        sumpv+=fcff/(1+wacc[k])**(t+0.5)
        fcff_last=fcff; nwc_prev=nwc; prev=core
    if wacc[k]-tgr[k]>0.005:
        tv=fcff_last*(1+tgr[k])/(wacc[k]-tgr[k]); pvtv=tv/(1+wacc[k])**8.5
        eq=sumpv+pvtv-NETDEBT
        prices[k]=eq/SHARES

mask=np.isfinite(prices)&(prices>0)&(prices<20000)
p=prices[mask]; nval=len(p)
pct={q:np.percentile(p,q) for q in [5,10,25,50,75,90,95]}
mean=p.mean(); std=p.std()
p_below=(p<CMP).mean()

print("="*54); print("  TITAN MONTE CARLO DCF v3 (reanchored FY25)"); print("="*54)
print(f"  Valid sims: {nval:,}/{N:,}   CMP: Rs {CMP:,.0f}")
print(f"  P5  Rs {pct[5]:,.0f}   P10 Rs {pct[10]:,.0f}   P25 Rs {pct[25]:,.0f}")
print(f"  P50 Rs {pct[50]:,.0f}  (median)   Mean Rs {mean:,.0f}")
print(f"  P75 Rs {pct[75]:,.0f}   P90 Rs {pct[90]:,.0f}   P95 Rs {pct[95]:,.0f}")
print(f"  P(fair value < CMP): {p_below:.1%}")

# correlations (tornado)
inp={'Revenue growth':g_shift[mask],'EBITDA margin':margin[mask],'WACC':wacc[mask],
     'Terminal growth':tgr[mask],'Inventory days':invd_shift[mask],'Capex %':capex_pct[mask],
     'Tax rate':tax[mask],'D&A %':da_pct[mask]}
corr={kk:stats.pearsonr(vv,p)[0] for kk,vv in inp.items()}
corr=dict(sorted(corr.items(),key=lambda x:abs(x[1]),reverse=True))
print("\n  SENSITIVITY (Pearson r):")
for kk,vv in corr.items(): print(f"   {kk:<18} {vv:+.3f}")

# ---- CHART (dark / cosmic) ----
plt.rcParams.update({'font.family':'DejaVu Sans'})
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(14,6)); fig.patch.set_facecolor('#0d1117')
for ax in (ax1,ax2):
    ax.set_facecolor('#0d1117')
    for s in ax.spines.values(): s.set_color('#30363d')
    ax.tick_params(colors='#c9d1d9'); ax.xaxis.label.set_color('#c9d1d9'); ax.yaxis.label.set_color('#c9d1d9')
ACC='#7c8cff'; GLD='#e3b341'; RED='#f85149'; GRN='#3fb950'
bins=np.linspace(p.min(),min(p.max(),4000),70)
n_h,be,patches=ax1.hist(p,bins=bins,color=ACC,alpha=0.9,edgecolor='#0d1117',linewidth=0.4)
for patch,left in zip(patches,be[:-1]):
    patch.set_facecolor(GRN if left<CMP else RED)
    patch.set_alpha(0.55)
ax1.axvline(pct[50],color=GLD,lw=2.5,label=f'Median  Rs {pct[50]:,.0f}')
ax1.axvline(CMP,color='#ff7b72',lw=2.5,ls='--',label=f'CMP  Rs {CMP:,.0f}')
ax1.axvspan(pct[10],pct[90],alpha=0.10,color=ACC)
ax1.set_title('Distribution of Implied Fair Value\n10,000 simulations — reanchored FY25 engine',
              color='#f0f6fc',fontsize=12,fontweight='bold',pad=12)
ax1.set_xlabel('Fair value per share (Rs)'); ax1.set_ylabel('Simulations')
ax1.legend(facecolor='#161b22',edgecolor='#30363d',labelcolor='#c9d1d9',fontsize=9)
box=(f"P10  Rs {pct[10]:,.0f}\nP50  Rs {pct[50]:,.0f}\nP90  Rs {pct[90]:,.0f}\n"
     f"P(FV<CMP) {p_below:.0%}")
ax1.text(0.97,0.97,box,transform=ax1.transAxes,va='top',ha='right',fontsize=9.5,color='#c9d1d9',
         bbox=dict(boxstyle='round,pad=0.5',facecolor='#161b22',edgecolor=ACC))
names=list(corr.keys()); vals=list(corr.values())
cols=[RED if v<0 else GRN for v in vals]
ax2.barh(names,vals,color=cols,alpha=0.85,edgecolor='#0d1117')
ax2.axvline(0,color='#8b949e',lw=0.8); ax2.set_xlim(-1,1)
ax2.set_title('Input Sensitivity (Pearson correlation)',color='#f0f6fc',fontsize=12,fontweight='bold',pad=12)
ax2.set_xlabel('Correlation with fair value')
ax2.invert_yaxis()
for i,v in enumerate(vals):
    ax2.text(v+(0.03 if v>=0 else -0.03),i,f'{v:.2f}',va='center',ha='left' if v>=0 else 'right',
             color='#c9d1d9',fontsize=9)
plt.suptitle('Titan Company (NSE: TITAN) — Monte Carlo DCF v3',color=GLD,fontsize=13,fontweight='bold',y=1.01)
plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/titan_montecarlo_v3.png',dpi=150,bbox_inches='tight',facecolor='#0d1117')
print("\n chart saved")

summary={"version":"v3_reanchored_FY25","n_valid":int(nval),"cmp":CMP,
  "median":round(float(pct[50])),"mean":round(float(mean)),
  "p10":round(float(pct[10])),"p25":round(float(pct[25])),"p75":round(float(pct[75])),"p90":round(float(pct[90])),
  "p_fv_below_cmp":round(float(p_below),4),
  "central_case_check":"Rs 1,013 vs deterministic Rs 1,017",
  "correlations":{k:round(v,3) for k,v in corr.items()}}
json.dump(summary,open('/mnt/user-data/outputs/montecarlo_summary_v3.json','w'),indent=2)
print(" json saved")
