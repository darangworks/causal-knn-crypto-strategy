# Results — Causal kNN Crypto Strategy (v1.2-frozen)

**Status:** Observations only. Interpretation belongs in `VERDICT.md`.
**Frozen tag:** `v1.2-frozen`
**Canonical source:** `REPORT.md` and `results/*.txt`

---

## 1. Frozen baseline (BTC 4H, full cost)

| Metric | Value |
|--------|-------|
| Trades | 131 |
| Gross PnL | +$3,803.16 |
| Total cost | −$1,802.77 |
| Net PnL | +$2,000.38 |
| Win rate | 38.17% |
| Profit factor | 1.095 |
| Identity check | OK |

Source: `results/btc_backtest.txt`

---

## 2. Causal / leakage validation

| Test | Result |
|------|--------|
| 7 causal-mechanics tests | 7/7 pass |
| Sympy accounting proof | Difference = 0, identity confirmed |
| Data integrity (SHA-256) | Verified against `data/MANIFEST.md` |

Sources: `tests/test_causal_knn_corrected.py`, `accounting/sympy_proof.py`,
`results/pytest_output.txt`, `results/sympy_output.txt`

---

## 3. Walk-forward (single 50/50 split)

Split at bar 2166. IS = first 50%, OOS = second 50%.

| Segment | Trades | Gross | Net (full cost) | Return % | WR % | PF |
|---------|--------|-------|------------------|----------|------|-----|
| IS | 58 | −$2,771 | −$3,573.68 | −3.57% | 27.59 | 0.682 |
| OOS | 57 | +$5,539 | +$4,733.23 | +4.73% | 45.61 | 1.564 |

Source: `results/walkforward.txt`

---

## 4. Chronological consistency windows (6 windows, BTC 4H)

| Fold | Period | Trades | Net | WR % | PF | IC |
|------|--------|--------|------|------|-----|-----|
| 1 | 2024-09-13 → 2025-01-11 | 13 | −$505 | 30.77 | 0.803 | −0.00425 |
| 2 | 2025-01-11 → 2025-05-11 | 11 | −$2,019 | 18.18 | 0.162 | −0.08030 |
| 3 | 2025-05-11 → 2025-09-08 | 10 | +$48 | 40.00 | 1.043 | +0.05490 |
| 4 | 2025-09-09 → 2026-01-13 | 14 | −$1,594 | 14.29 | 0.470 | +0.02810 |
| 5 | 2026-01-13 → 2026-05-14 | 16 | −$22 | 37.50 | 0.991 | −0.06803 |
| 6 | 2026-05-14 → 2026-09-12 | 9 | +$1,295 | 55.56 | 2.559 | +0.00972 |

Positive folds: 2/6. Total net: −$2,796.09. t-stat (mean per fold): −0.948.

Source: `results/btc_kfold.txt`

---

## 5. Cross-asset validation (BTC / ETH / SOL, 6 windows each)

| Symbol | Folds + | Trades | Total Gross | Total Net | Mean/fold | t-stat |
|--------|---------|--------|-------------|-----------|-----------|--------|
| BTC-USD | 2/6 | 73 | −$1,774 | −$2,796 | −$466 | −0.948 |
| ETH-USD | 3/6 | 75 | +$222 | −$834 | −$139 | −0.381 |
| SOL-USD | 2/6 | 82 | −$3,050 | −$4,192 | −$699 | −1.995 |

Source: `results/crossasset.txt`

---

## 6. Predictive diagnostics / IC

Unconditional IC (BTC 4H, N = 3,977):

| Metric | Value |
|--------|-------|
| Pearson IC | −0.02800 |
| Spearman IC | −0.02912 |
| Directional accuracy | 48.63% |
| ACF block length (auto) | 140 |

Prediction quintiles (mean return per quintile):

| Quintile | Mean return | N |
|----------|-------------|---|
| Q1 | +0.0475% | 796 |
| Q2 | −0.0134% | 795 |
| Q3 | +0.0325% | 795 |
| Q4 | −0.0474% | 795 |
| Q5 | −0.0325% | 796 |

Q5 − Q1 spread: −0.0800%. Rank correlation (Q, mean): −0.800.

Source: `results/btc_backtest.txt`

---

## 7. Cost sensitivity (BTC 4H)

| Scenario | Trades | Gross | Total cost | Net |
|----------|--------|-------|------------|-----|
| Zero cost | 132 | +$4,656.89 | $0 | +$4,656.89 |
| Commission only | 132 | +$4,590.95 | −$1,303.19 | +$3,287.76 |
| Slippage only | 131 | +$3,860.71 | −$518.43 | +$3,342.28 |
| Full cost | 131 | +$3,803.16 | −$1,802.77 | +$2,000.38 |

Source: `results/btc_backtest.txt`

---

## 8. Baseline 1H reference

628 trades, net −$8,805.86 (full cost).

Source: `results/baseline_1h.txt`

---

## 9. Reproducibility / parity observations

| Check | Result |
|-------|--------|
| 7 causal-mechanics tests | 7 passed |
| Sympy accounting proof | Difference = 0 |
| Data SHA-256 verification | Match |
| Internet required for frozen results | No |

Tolerances for reproduction are specified in `REPRODUCIBILITY.md`.

---

## Source files (canonical)

| File | Content |
|------|---------|
| `results/btc_backtest.txt` | Cost scenarios + IC + quintiles |
| `results/walkforward.txt` | Single 50/50 split |
| `results/btc_kfold.txt` | 6 chronological windows |
| `results/crossasset.txt` | BTC / ETH / SOL |
| `results/baseline_1h.txt` | 1H reference |
| `results/pytest_output.txt` | Test output |
| `results/sympy_output.txt` | Sympy output |
| `REPORT.md` | Full narrative + tables |
| `REPRODUCIBILITY.md` | Reproduction procedure |