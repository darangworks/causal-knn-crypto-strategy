# Methodology — Causal kNN Crypto Strategy (v1.2-frozen)

**Frozen tag:** `v1.2-frozen`
**Canonical source:** `REPORT.md` sections 2, 3, 4.
**Purpose:** Describe the causal reconstruction, verification pipeline,
and validation layers as implemented in v1.2-frozen.

---

## 1. Source analysis

The source indicator (Zeiierman, "AI Predictive Flow", Pine Script,
CC BY-NC-SA 4.0) contained two implementation-level issues:

### Issue 1 — Backward target
`y = log(base) - log(base[ahead])` in Pine Script uses historical
(not future) values for `[ahead]`. The nominal target therefore
becomes a backward return.

### Issue 2 — Self-contamination
The current pattern was inserted into training memory before
prediction, making the query its own neighbor.

Source: `REPORT.md` §2.

---

## 2. Causal reconstruction

Four changes:

1. **Delayed labels** — pattern at `t − AHEAD`, label to `t`.
2. **No self-inclusion** — current bar never in its own training memory.
3. **Feature normalization** — ATR-normalized features.
4. **Bounded memory + normalized inverse-distance weighting** — finite
   ring buffer, normalized weights.

Source: `REPORT.md` §3.

---

## 3. Verification pipeline

### 3.1 Seven causal-mechanics tests
Delayed labels, no self-contamination, no future information in
training, and behavior under randomized input. Result: 7/7 pass.
Sources: `tests/test_causal_knn_corrected.py`, `results/pytest_output.txt`.

### 3.2 SymPy accounting proof
Two formulations of the final equity (baseline vs. v2) are shown to
be algebraically identical. Result: `Difference = 0`, identity confirmed.
Sources: `accounting/sympy_proof.py`, `results/sympy_output.txt`.

### 3.3 Data integrity
Frozen CSVs with SHA-256 hashes in `data/MANIFEST.md`. Result: hashes match.
Sources: `data/MANIFEST.md`, `REPRODUCIBILITY.md`.

---

## 4. Validation layers

### 4.1 Single backtest (BTC 4H)
Four cost scenarios: zero, commission only, slippage only, full cost.
Identity check enforced per scenario.
Sources: `src/diagnostic_v11_4h_notrail.py`, `results/btc_backtest.txt`.

### 4.2 Walk-forward (single 50/50)
Chronological split at bar 2166. Both segments reported with the same
cost model.
Sources: `validation/diagnostic_v13_walkforward.py`, `results/walkforward.txt`.

### 4.3 Chronological consistency windows
6 equal windows per asset (BTC, ETH, SOL).
Sources: `validation/diagnostic_v14_kfold.py`, `results/btc_kfold.txt`.

### 4.4 Cross-asset
Same specification applied to BTC-USD, ETH-USD, SOL-USD on 4H.
Sources: `validation/diagnostic_v15_crossasset.py`, `results/crossasset.txt`.

### 4.5 Predictive diagnostics
Pearson IC, Spearman IC, directional accuracy, prediction quintiles,
ACF-based block length.
Source: `results/btc_backtest.txt`.

---

## 5. Data contract

**Version:** v1
**Frozen:** 2026-09-12

1. No changes to strategy, features, thresholds, kNN parameters,
   filters, or execution logic may be made based solely on the
   frozen results.
2. Any required change is `Frozen v2`, not a modification of v1.
3. `freeze_data.py` must not be run against the current snapshot.
4. Tolerances for reproduction are specified in `REPRODUCIBILITY.md`.

---

## 6. Reproduction

See `REPRODUCIBILITY.md` for the step-by-step procedure.
No internet access is required for frozen-result reproduction.