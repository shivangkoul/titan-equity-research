"""
TITAN — Phase 4: LLM Earnings-Call Sentiment Scoring  ->  bounded DCF overlay
=============================================================================
Scores management CONFIDENCE from earnings-call transcripts using Groq (LLaMA),
across 5 analyst dimensions, builds a quarterly trend, and maps the latest
reading to a TIGHTLY BOUNDED adjustment of the stage-1 revenue-growth assumption.

Design principle (why this is defensible, not a gimmick):
  - Sentiment is a SUPPLEMENTARY signal, never a core driver.
  - Max influence is +/-1.5pp on near-term growth. It cannot move the thesis.
  - Every score carries a one-line textual basis (no black-box numbers).
  - We always report valuation WITH and WITHOUT the overlay, so its effect is visible.

Usage:
  pip install groq
  set GROQ_API_KEY=...           (PowerShell:  $env:GROQ_API_KEY="...")
  python groq_sentiment.py                 # live, reads ./transcripts/*.txt
  python groq_sentiment.py --mock          # offline pipeline test, no API
"""
import os, re, json, glob, argparse

MODEL = "llama-3.3-70b-versatile"   # Groq

DIMENSIONS = {
 "demand_outlook":   "Forward confidence on consumer demand (jewellery/watches). Cautious/'challenging' -> negative.",
 "margin_guidance":  "Confidence on margin trajectory (esp. gold customs-duty / studded mix). Defensive -> negative.",
 "growth_ambition":  "Conviction in store expansion, market-share gains, explicit guidance.",
 "execution":        "Evidence of delivering on prior guidance; credibility of management.",
 "hedging_language": "Density of hedging/uncertainty qualifiers. MORE hedging -> negative score.",
}

SYSTEM = (
 "You are a sell-side equity analyst scoring an earnings-call transcript for MANAGEMENT CONFIDENCE. "
 "Be skeptical and literal. Score ONLY from the text; do not use outside knowledge. "
 "Each dimension is scored -2 (very negative) to +2 (very positive), integers allowed plus 0. "
 "Return STRICT JSON only, no prose, no markdown fences."
)

def build_prompt(transcript):
    dims = "\n".join(f'  "{k}": <-2..2 int>,   // {v}' for k,v in DIMENSIONS.items())
    return (
      f"Score this earnings-call transcript. Return JSON exactly of the form:\n"
      f"{{\n  \"scores\": {{\n{dims}\n  }},\n"
      f"  \"basis\": {{ \"<dimension>\": \"<=15-word justification quoting/paraphrasing the text\" }}\n}}\n\n"
      f"TRANSCRIPT (management commentary + Q&A):\n\"\"\"\n{transcript[:14000]}\n\"\"\""
    )

def call_groq(transcript):
    from groq import Groq
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    resp = client.chat.completions.create(
        model=MODEL, temperature=0,
        response_format={"type":"json_object"},
        messages=[{"role":"system","content":SYSTEM},
                  {"role":"user","content":build_prompt(transcript)}],
    )
    return json.loads(resp.choices[0].message.content)

def mock_score(transcript):
    """Deterministic offline stand-in: crude lexicon so the PIPELINE is testable."""
    t = transcript.lower()
    pos = sum(t.count(w) for w in ["strong","robust","confident","record","healthy","momentum","accelerat","outperform","double-digit","expand"])
    neg = sum(t.count(w) for w in ["challeng","headwind","cautious","subdued","pressure","weak","decline","uncertain","soft","moderat"])
    base = max(-2, min(2, round((pos-neg)/4)))
    sc = {k: base for k in DIMENSIONS}
    sc["hedging_language"] = max(-2, min(2, -round(neg/3)))   # more hedging -> negative
    return {"scores": sc, "basis": {k: f"[mock] pos={pos} neg={neg}" for k in DIMENSIONS}}

def mci(scores):
    """Aggregate to Management Confidence Index in [-1,+1]."""
    vals = [scores[k] for k in DIMENSIONS]
    return sum(vals) / (2*len(vals))   # each in [-2,2] -> normalise

def growth_overlay(latest_mci, cap=0.015):
    """Bounded stage-1 growth adjustment. |overlay| <= cap (1.5pp)."""
    return round(latest_mci * cap, 4)

# ---- bounded FV impact via the verified central engine ----
def central_fv(stage1_growth_adj=0.0):
    CORE=57332.; INV,REC,PAY,OCL,GOLD=28184.,1068.,1963.,4441.,7810.
    NETDEBT=11223.; SH=88.8
    g=[0.306,0.16,0.14,0.125,0.115,0.10,0.085,0.07,0.055]
    g=[gx+(stage1_growth_adj if 1<=i<=4 else 0) for i,gx in enumerate(g)]  # nudge FY27-30
    m=[0.109,0.111,0.113,0.114,0.115,0.115,0.115,0.115,0.115]
    invd=[165,163,161,159,157,156,155,154,153]
    DA,CX,TAX,W,TGR=0.012,0.013,0.255,0.122,0.055
    nwc_prev=INV+REC-PAY-OCL-GOLD; prev=CORE; sumpv=0; last=0
    for t in range(9):
        core=prev*(1+g[t]); ebit=core*m[t]-core*DA; nopat=ebit*(1-TAX)
        inv=core/365*invd[t]; nwc=inv+core/365*7-core/365*12-core*0.08-inv*0.28
        fcff=nopat+core*DA-core*CX-(nwc-nwc_prev)
        sumpv+=fcff/(1+W)**(t+0.5); last=fcff; nwc_prev=nwc; prev=core
    tv=last*(1+TGR)/(W-TGR); ev=sumpv+tv/(1+W)**8.5
    return (ev-NETDEBT)/SH

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--mock",action="store_true"); a=ap.parse_args()
    files=sorted(glob.glob(os.path.join(os.path.dirname(__file__),"transcripts","*.txt")))
    if not files: print("No transcripts in ./transcripts/*.txt"); return
    scorer = mock_score if a.mock else call_groq
    rows=[]
    for f in files:
        txt=open(f,encoding="utf-8",errors="ignore").read()
        label=re.sub(r"\.txt$","",os.path.basename(f))
        out=scorer(txt); m=mci(out["scores"])
        rows.append({"quarter":label,"mci":round(m,3),"scores":out["scores"]})
        print(f"{label:<12} MCI={m:+.2f}  {out['scores']}")
    latest=rows[-1]["mci"]; ov=growth_overlay(latest)
    base_fv=central_fv(0.0); adj_fv=central_fv(ov)
    print(f"\nLatest MCI: {latest:+.2f}  ->  stage-1 growth overlay: {ov*100:+.2f}pp (capped +/-1.5pp)")
    print(f"Fair value  base: Rs {base_fv:,.0f}   sentiment-adjusted: Rs {adj_fv:,.0f}   (delta Rs {adj_fv-base_fv:+,.0f})")
    json.dump({"transcripts":rows,"latest_mci":latest,"growth_overlay_pp":ov*100,
               "fv_base":round(base_fv),"fv_sentiment_adj":round(adj_fv)},
              open(os.path.join(os.path.dirname(__file__),"sentiment_results.json"),"w"),indent=2)

if __name__=="__main__": main()
