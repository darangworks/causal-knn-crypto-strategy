
# Causal Reconstruction and Validation of Zeiierman's "AI Predictive Flow" Indicator as a Trading Strategy

**A Negative Result with Reusable Methodology**

**Author:** Mohammad Darang
**Date:** September 2026
**Version:** 1.2 (frozen data revision)
**Data Snapshot:** 2026-09-12 (see `data/MANIFEST.md` for SHA-256)
**Source Indicator:** [AI Predictive Flow (Zeiierman)](https://www.tradingview.com/script/qaaxkW1P-AI-Predictive-Flow-Zeiierman/) — CC BY-NC-SA 4.0

---

## Abstract

We attempted to convert Zeiierman's open-source kNN-based oscillator into a systematic trading strategy. The original indicator contains two critical issues when interpreted as a predictive model: a backward-looking target variable and self-contamination of the training set. We rebuilt the pipeline with strict causal discipline, verified it with a 7-test leakage suite, established symbolic equivalence between two accounting formulations with sympy, and ran a multi-stage validation sequence (walk-forward, chronological consistency windows, cross-asset robustness).

**Result:** No robust evidence of economically significant predictive performance was found under the tested specification and validation procedures. The single positive full-sample BTC 4H result (+$2,000.38 after stated costs) is not supported by temporal consistency, predictive IC, or cross-asset validation. We document the methodology, findings, and reusable diagnostic infrastructure.

---

## 1. Introduction

### 1.1 Source Indicator

Zeiierman's "AI Predictive Flow" constructs a 4-feature vector at each bar:

| Feature | Formula | Interpretation |
|---------|---------|----------------|
| f1 | log(close / close[1]) | Log return |
| f2 | (close − close[5]) / close[5] | 5-bar momentum |
| f3 | (RSI(14) − 50) / 50 | Centered RSI |
| f4 | (EMA(10) − EMA(30)) / close | EMA spread |

The `k` nearest historical patterns (by Euclidean distance) are weighted to produce a prediction, smoothed into an oscillator.

### 1.2 Research Question

Does this causal reconstruction exhibit robust predictive or economic performance under the specified 4H crypto-market configuration and validation procedures?

### 1.3 Answer

No robust evidence was detected under this specification.

---

## 2. Source Analysis

### 2.1 Issue #1 — Backward Target

```pine
y := math.log(base) - math.log(base[ahead])
```

In Pine Script, `[ahead]` is a **historical** offset. This computes a backward return, not a forward return.

### 2.2 Issue #2 — Self-Contamination

The current pattern is inserted into training *before* prediction. The query is its own nearest neighbor.

### 2.3 Scope

These issues concern the indicator's interpretation as a predictive model. They do not by themselves establish that the indicator is unsuitable as a visualization tool.

---

## 3. Causal Reconstruction

### 3.1 Delayed Training

```python
train_end = i - AHEAD
vec   = features[train_end - PATTERN_LEN + 1 : train_end + 1]
label = log(close[i] / close[train_end])
add_to_memory(vec, label)
query = features[i - PATTERN_LEN + 1 : i + 1]
pred  = knn(query)
```

### 3.2 Feature Normalization

All features divided by ATR, clipped to [−5, 5].

### 3.3 Bounded Memory

Flat arrays with ring buffer. No matrices, no unbounded growth.

### 3.4 Normalized Inverse-Distance Weighting

```python
weights = 1.0 / (distances + 1e-6)
pred = (weights * Y).sum() / weights.sum()
```

---

## 4. Verification and Validation Pipeline

**Verification** asks: does the code execute what was intended?
**Validation** asks: does what was executed carry an edge?

### 4.1 Seven Causal-Mechanics Tests (7/7 PASS)

The test suite verifies **causal mechanics** (delayed labels, bounded memory, no self-contamination) using a reference implementation. The reference implementation uses a momentum proxy for feature f3 instead of production RSI, to keep tests independent of pandas ta-lib. The tests are designed to verify causal mechanics rather than the numerical implementation of the production feature set.

| # | Test | Result |
|---|------|:------:|
| 1 | Current bar never in training | PASS |
| 2 | Labels are forward returns | PASS |
| 3 | Ring buffer bounded | PASS |
| 4 | Normalized IDW | PASS |
| 5 | No prediction before k samples | PASS |
| 6 | Random walk → no edge | PASS |
| 7 | Determinism | PASS |

**Test 6 — Random-Walk Oracle Scope:** The random-walk oracle passed under the predefined tolerance thresholds. This provides evidence against certain forms of implementation leakage, but does **not** constitute a formal proof of leakage absence across the entire pipeline.

### 4.2 Symbolic Equivalence Proof for the Two Accounting Formulations

Verified with sympy: `E_final_baseline − E_final_v2 = 0` as an algebraic identity.

**Scope:** This proof establishes algebraic equivalence between the two specified accounting formulations. It is **not** a proof of correctness of the entire backtesting engine, position sizing, execution logic, or commission application.

### 4.3 Data Integrity

All datasets frozen with full SHA-256 hashes. See `data/MANIFEST.md`.

| Symbol | Interval | Rows | First | Last |
|--------|:--------:|:----:|-------|------|
| BTC-USD | 4h | 4,333 | 2024-09-13 | 2026-09-12 |
| ETH-USD | 4h | 4,333 | 2024-09-13 | 2026-09-12 |
| SOL-USD | 4h | 4,333 | 2024-09-13 | 2026-09-12 |
| BTC-USD | 1h | 17,318 | 2024-09-13 | 2026-09-12 |

---

## 5. Experimental Results

All numbers below are from the frozen data snapshot. No number is assumed to be preserved from pre-freeze runs.

### 5.1 Best-Configuration Backtest (BTC 4H)

| Scenario | Trades | Gross | Net | WR | PF |
|----------|:------:|:-----:|:---:|:--:|:--:|
| Zero Cost | 132 | +$4,656.89 | +$4,656.89 | 38.64% | 1.230 |
| Commission Only | 132 | +$4,590.95 | +$3,287.76 | 38.64% | 1.157 |
| Slippage Only | 131 | +$3,860.71 | +$3,342.28 | 38.17% | 1.163 |
| **Full Cost** | **131** | **+$3,803.16** | **+$2,000.38** | **38.17%** | **1.095** |

**Information Coefficient (full sample):**
- Pearson IC: −0.02800
- Spearman IC: −0.02912
- Directional Accuracy: 48.63%
- ACF block length (auto): 140

**Quintile structure (prediction vs. forward return):**

| Quintile | Mean Fwd Return |
|:--------:|:---------------:|
| Q1 (lowest pred) | +0.0475% |
| Q2 | −0.0134% |
| Q3 | +0.0325% |
| Q4 | −0.0474% |
| Q5 (highest pred) | −0.0325% |
| **Q5 − Q1** | **−0.0800%** |

Rank correlation (Q, mean): **−0.800**

**Observation:** The quintile structure is not monotonic and has the opposite sign from what a predictive model would produce. IC is negative. The positive net PnL does not appear to come from a monotonic predictive signal.

### 5.2 Ablation Studies

| Configuration | Zero-Cost Gross PnL | Relative to Full |
|---------------|:-------------------:|:----------------:|
| kNN + MTF | +$5,537 (pre-freeze reference) | — |
| Constant prediction | +$811 (pre-freeze) | ~85% lower |
| No MTF | +$376 (pre-freeze) | ~93% lower |

Note: Ablation figures are from the pre-freeze snapshot and are reported here for context only. They are not part of the frozen v1.2 results.

### 5.3 Walk-Forward (Single 50/50 Split)

| Period | Trades | Net | Return % | WR | PF |
|--------|:------:|:---:|:--------:|:--:|:--:|
| In-Sample | 58 | **−$3,573.68** | −3.57% | 27.59% | 0.682 |
| Out-of-Sample | 57 | **+$4,733.23** | +4.73% | 45.61% | 1.564 |

OOS IC: +0.00034 · OOS DA: 49.75% · OOS ACF block: 148

**VERDICT (engine output):** `[WARN] IS negative AND OOS positive → possible luck`

**Interpretation:** The positive OOS result is a single realization. The absence of predictive IC (+0.00034) and the negative IS result make a luck/regime explanation plausible. The OOS result alone is not evidence of generalization.

### 5.4 Chronological Consistency Windows (6 windows, BTC 4H)

Each window is treated as an independent experiment with a fresh kNN memory buffer. This is **not** a rolling walk-forward. The design measures consistency of behavior across time periods, not cumulative learning.

| Window | Period | Trades | Gross | Net | WR | PF | IC |
|:------:|--------|:------:|:-----:|:---:|:--:|:--:|:--:|
| 1 | 2024-09-13 → 2025-01-11 | 13 | −$322 | −$505 | 30.77% | 0.803 | −0.004 |
| 2 | 2025-01-11 → 2025-05-11 | 11 | −$1,867 | −$2,019 | 18.18% | 0.162 | −0.080 |
| 3 | 2025-05-11 → 2025-09-08 | 10 | +$188 | +$48 | 40.00% | 1.043 | +0.055 |
| 4 | 2025-09-09 → 2026-01-13 | 14 | −$1,400 | −$1,594 | 14.29% | 0.470 | +0.028 |
| 5 | 2026-01-13 → 2026-05-14 | 16 | +$204 | −$22 | 37.50% | 0.991 | −0.068 |
| 6 | 2026-05-14 → 2026-09-12 | 9 | +$1,423 | +$1,295 | 55.56% | 2.559 | +0.010 |
| **Total** | | **73** | **−$1,774** | **−$2,796** | | | |

**Positive windows:** 2/6 (33.3%) · **Verdict:** WEAK

### 5.5 Cross-Asset Robustness Check

| Symbol | Windows+ | Trades | Total Gross | Total Net | Mean/Window | t-stat | Verdict |
|:------:|:--------:|:------:|:-----------:|:---------:|:-----------:|:------:|:-------:|
| BTC-USD | 2/6 | 73 | −$1,774 | −$2,796 | −$466 | −0.948 | WEAK |
| ETH-USD | 3/6 | 75 | +$222 | −$834 | −$139 | −0.381 | WEAK |
| SOL-USD | 2/6 | 82 | −$3,050 | −$4,192 | −$699 | −1.995 | WEAK |

**Final Verdict:** `[FAIL] No asset shows consistent edge`

Note: The t-statistics are based on only six windows per asset and should not be interpreted as strong evidence for or against an edge.

### 5.6 Baseline 1H (Reference)

| Metric | Value |
|--------|-------|
| Trades | 628 |
| Net PnL | **−$8,805.86** |
| Return | **−8.81%** |
| Profit Factor | 0.776 |
| Win Rate | 32.01% |
| Max Drawdown | −10.44% |
| Sharpe | −1.64 |

**Interpretation:** The 1H baseline is unprofitable under the same accounting and execution model.

---

## 6. Statistical Summary

### 6.1 Information Coefficient

| Period | Pearson IC | Spearman IC | N |
|--------|:----------:|:-----------:|:-:|
| Full sample (BTC 4H) | −0.02800 | −0.02912 | 3,977 |
| IS (BTC 4H) | — | −0.05078 | 1,810 |
| OOS (BTC 4H) | — | +0.00034 | 1,811 |

IC is negative on the full sample and unstable across windows. In OOS, IC is essentially zero.

### 6.2 Effective Sample Size

Recomputation is pending a formally defined ESS methodology. No number is reported until that is finalized.

### 6.3 Sharpe Definition

Sharpe ratios in this report are computed as:

```
Sharpe = mean(equity.pct_change()) / std(equity.pct_change()) 
         × sqrt(24 × 365)
```

where returns are measured on the **hourly equity curve**, not on position-level returns. Since the strategy deploys only 10% of equity per trade and is flat most of the time, this Sharpe is **not directly comparable** to Sharpe computed on fully-invested exposure.

This metric definition is fixed for all backtests and reported consistently.

### 6.4 t-Statistic (6 windows, BTC 4H)

```
Mean net per window: −$466.01
Std net per window:  $1,204.00
SE = $1,204.00 / √6 = $491.53
t = −$466.01 / $491.53 = −0.948
```

---

## 7. Methodological Issues Raised by Independent Audits

Five methodological issues were raised across three separately prompted AI evaluations:

1. **Multiple testing / selection bias** — ~15 configurations were explored during research; the reported configuration was selected after exploratory iteration. Naive p-values are invalid.
2. **Effective sample size** — ESS recomputation pending formal methodology.
3. **Walk-forward design** — single 50/50 split provides only one OOS realization.
4. **Costs not stress-tested** — single cost scenario given edge magnitude is close to cost magnitude.
5. **Purging/embargo** — feature and label windows can span adjacent windows in chronological validation.

---

## 8. Limitations

1. **Sample size:** ~73 trades per asset over 2 years
2. **Effective N:** pending recomputation
3. **Regime coverage:** 2 years only; no full bear market
4. **Feature space:** four price-derived features (return, momentum, RSI, EMA spread); broader feature families were not explored
5. **Model class:** kNN only; no non-linear model benchmarks
6. **Cost assumptions:** single scenario; sensitivity not yet evaluated

---

## 9. AI Assistance Disclosure

### Development Phase

| Model | Role |
|-------|------|
| DeepSeek | Early strategy critique |
| Qwen | Parallel architecture evaluation |
| One additional chat model | Final phase |

Each AI-assisted development workflow produced at least one material error that was subsequently detected through independent verification. See Appendix C.

### Evaluation Phase

Three separately prompted AI evaluations (ChatGPT, Claude Sonnet 5, Grok) with identical prompts. Raw responses preserved in `evaluations/`.

AI can accelerate research, but verification remains necessary.

---

## 10. Conclusions

Under the specified causal reconstruction, feature set, 4H frequency, assets, execution assumptions, and tested validation procedures, **we found no robust evidence of economically significant predictive performance.**

The apparent positive full-sample BTC 4H result (+$2,000.38 after stated costs) is **not supported by**:
- temporal consistency (2/6 windows positive)
- predictive IC (negative on full sample, near-zero in OOS)
- cross-asset validation (all three assets WEAK)
- quintile structure (non-monotonic, rank correlation −0.800)

The 1H baseline is unprofitable. The positive OOS result in the fixed split remains compatible with regime effects or sampling luck.

**This conclusion is scoped to the tested configuration.** It does not establish that the underlying feature representation carries no information at other horizons, on other asset classes, or with different model classes.

---

## 11. Recommended Next Steps

The following steps are prerequisites for any further evaluation:

1. Complete the pending ESS methodology
2. Add purging/embargo to chronological windows
3. Run rolling walk-forward validation with multiple OOS periods
4. Stress-test transaction costs (0–20 bp round-trip)
5. Quantify and correct for configuration selection bias
6. **Only then** evaluate alternative feature families or model classes

---

## 12. Artifacts

### Validation Scripts (frozen v1.2)
- `src/diagnostic_v11_4h_notrail.py`
- `validation/diagnostic_v13_walkforward.py`
- `validation/diagnostic_v14_kfold.py`
- `validation/diagnostic_v15_crossasset.py`
- `src/run_local_baseline.py`

### Verification
- `tests/test_causal_knn_corrected.py`
- `accounting/sympy_proof.py`

### Data
- `data/MANIFEST.md`
- `data/*.csv` (frozen snapshots)

### Results (frozen v1.2)
- `results/*.txt`

### Metadata
- `research_log/configurations.md`
- `evaluations/chatgpt.md`, `claude.md`, `grok.md`
- `LICENSE-MAP.md`

### Not part of reproduction
- `freeze_data.py` (used once to create the frozen snapshot; not part of the reproduction path)

---

## Appendix A — Diagnostic Sequence

The following steps were used during development. Only steps marked with ✅ are part of the frozen v1.2 validation suite and reported in this document.

```
✅ 1. Causal correctness (7 leakage tests)
✅ 2. Accounting equivalence (sympy proof of two formulations)
✅ 3. Unconditional IC + directional accuracy
✅ 4. Walk-forward (50/50 split)
✅ 5. Chronological consistency windows (6 windows)
✅ 6. Cross-asset robustness (BTC / ETH / SOL)

   • Execution parity against Pine baseline was performed during 
     development but is not part of the frozen validation suite. 
     No frozen artifact is provided for this step.
   • Ablation studies (constant prediction, no-MTF) were performed 
     pre-freeze and are reported for context only.
```

Live deployment was not considered part of this study.

---

## Appendix B — Anti-Patterns Avoided

- ❌ Optimize parameters on full history
- ❌ Report a single backtest number
- ❌ Ignore transaction costs
- ❌ Use close for stop checks (must be high/low)
- ❌ Insert current pattern into training
- ❌ Trust Sharpe from one period

**Even with all these avoided, no robust edge was found.**

---

## Appendix C — Four Documented AI Development Errors

### Error 1 — False lookahead claim about Pine Script semantics

**AI claimed:** `base[ahead]` in Pine Script is a future reference.
**Reality:** `[ahead]` is a historical offset.
**Detection:** Manual review of Pine Script documentation.
**Impact:** Would have invalidated the audit report.

### Error 2 — Phantom accounting bug

**AI claimed:** A double-counting bug in entry commission.
**Reality:** The two accounting formulations were algebraically equivalent (verified with sympy).
**Detection:** Symbolic proof.
**Impact:** Would have triggered unnecessary code changes.

### Error 3 — "Flawless" verdict on contaminated code

**AI claimed:** An early version was "flawless."
**Reality:** It had self-contamination.
**Detection:** Random-walk oracle test.
**Impact:** Would have led to a false positive backtest.

### Error 4 — Silent feature set change

**AI claimed:** A diagnostic script comparable to baseline.
**Reality:** Features f3 and f4 were silently permuted.
**Detection:** Cross-check of feature parity.
**Impact:** Would have produced IC values for a different model.

These errors motivated the verification pipeline. Without it, an AI-generated backtest would have looked "profitable."

**Lesson:** AI-generated research code requires independent verification.

---

*End of Report (v1.2 — frozen data revision)*

