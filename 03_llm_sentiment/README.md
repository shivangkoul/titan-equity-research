# Phase 4 — LLM Earnings-Call Sentiment Scoring (Groq)

Quantifies management confidence from Titan earnings-call transcripts and maps it
to a **bounded** adjustment of the DCF's stage-1 revenue-growth assumption.

## What it does
1. Reads transcripts from `./transcripts/*.txt` (one per quarter, e.g. `FY26Q4.txt`).
2. Sends each to Groq (LLaMA-3.3-70B) with a structured analyst prompt.
3. Scores 5 dimensions (-2..+2): demand outlook, margin guidance, growth ambition,
   execution, hedging language. Each score carries a one-line textual basis.
4. Aggregates to a Management Confidence Index (MCI) in [-1, +1], builds a quarterly trend.
5. Maps the latest MCI to a stage-1 growth overlay, **capped at +/-1.5pp**.
6. Reports fair value WITH and WITHOUT the overlay so its (small) effect is transparent.

## Why it is defensible (not a gimmick)
- Sentiment is a *supplementary* signal. Hard cap of +/-1.5pp means it cannot move the thesis.
- Every score has a textual basis — no black-box numbers.
- We always show base vs sentiment-adjusted FV. In the sample run a max-confident
  call moved FV only Rs 1,013 -> Rs 1,051 (+3.7%). Titan stays far below CMP.

## How to run (Windows / PowerShell)
```
pip install groq
$env:GROQ_API_KEY="your_key_here"
python groq_sentiment.py            # live
python groq_sentiment.py --mock     # offline pipeline test (no API, crude lexicon)
```

## Getting real transcripts
Titan concall transcripts: screener.in (Titan -> Documents -> Concalls) or the
Titan IR site (Investors -> Quarterly Results -> earnings-call transcript PDF).
Paste the management-commentary + Q&A text into a `.txt` per quarter. ~6 quarters
gives a meaningful confidence trend.

## Output
`sentiment_results.json` — per-quarter scores, latest MCI, growth overlay, base vs adjusted FV.

## Interview framing
"I score management confidence with an LLM but cap its influence at +/-1.5pp on
near-term growth, and always report the unadjusted value alongside. It refines the
estimate; it does not drive the conclusion."
