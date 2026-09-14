# Verdict — Causal kNN Crypto Strategy (v1.2-frozen)

**Frozen tag:** `v1.2-frozen`
**Date:** 2026-09-14
**Scope:** Zeiierman's "AI Predictive Flow" indicator, causally reconstructed
and tested on BTC-USD 4H (cross-checked on ETH-USD, SOL-USD, and BTC-USD 1H).

This document states what the evidence means. Facts and numbers are in
`RESULTS.md`.

---

## Verdict

> **No robust evidence of economically significant predictive
> performance was established under the tested specification.**

The single full-sample positive result (+$2,000.38 net on BTC 4H, 131
trades) is not supported by:

- temporal consistency (2/6 chronological windows positive),
- cross-asset robustness (BTC, ETH, SOL all WEAK),
- predictive information content (Pearson IC = −0.028, Spearman IC = −0.029),
- or walk-forward behavior (IS negative, OOS positive — the OOS positive
  is a single realization, not evidence of persistence).

---

## Three-concept separation

### 1. Causal validity
The reconstructed indicator passed all 7 causal-mechanics tests, the
SymPy accounting proof, and SHA-256 data integrity checks. These are
statements about the **tested** leakage pathways and accounting
identities — not about all possible leakage.

### 2. Out-of-sample evidence
Walk-forward (single 50/50): IS 58 trades −$3,573.68; OOS 57 trades
+$4,733.23 (full cost). Project 1's verdict is based on the conjunction
of single-split, chronological-window, and cross-asset results — all of
which fail to support the single-split OOS positive.

### 3. Statistical / inferential notes
- IC is negative (Pearson −0.028; Spearman −0.029).
- 6-window mean net is negative for all three assets.
- t-statistic (mean per window, BTC) = −0.948.
- The +$2,000 full-sample BTC result is not reproduced on ETH or SOL.

---

## What this document does NOT claim

- Does not claim the strategy has no edge in general.
- Does not claim the underlying indicator is meaningless.
- Does not claim the methodology generalizes to all pattern-matching
  strategies.
- Does not promote the strategy beyond exploratory status.

## What this document does claim

1. The causal reconstruction removes the two source-level issues
   (backward target, self-contamination).
2. The verification pipeline (leakage tests, SymPy proof, SHA-256
   integrity) functions as intended.
3. Under the tested specification, no robust evidence of predictive
   performance was found.
4. The transferable output is the verification methodology, not the
   strategy.

---

## Caveats

- Single walk-forward split; no purging or embargo.
- 6 chronological windows per asset; small-sample inference.
- Cross-asset list limited to BTC, ETH, SOL.
- Full-sample BTC result is one realization under one split.

---

## Recommendation

**Close this investigation.** Any variation (different k, thresholds,
filters, market) constitutes a new study with its own pre-registration.

The reusable asset is the **verification pipeline**.