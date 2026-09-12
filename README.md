
# Causal kNN Crypto Strategy — Negative Result

A causal reconstruction and validation study of Zeiierman's 
"AI Predictive Flow" indicator as a systematic trading strategy.

**Result:** No robust evidence of economically significant predictive 
performance under the tested specification.

**Contribution:** A reusable verification pipeline for pattern-matching 
strategies — including leakage tests, symbolic accounting proof, and 
a fully documented negative result.



## TL;DR

| Research stage | What happened |
|---------------|---------------|
| Configurations explored | ~15 |
| Best apparent full-sample result | +$2,000.38 net (BTC 4H, full cost) |
| Walk-forward OOS | +$4,733.23 (single realization) |
| Chronological windows (BTC 4H) | 2/6 positive, total −$2,796 |
| Cross-asset (BTC / ETH / SOL) | All three WEAK |
| Predictive IC (BTC 4H) | Pearson −0.028, OOS near zero |
| 1H Baseline | −$8,806 net |
| **Current conclusion** | **No robust edge detected under this specification** |

---

## What This Repo Contains

1. **Causal kNN implementation** with delayed labels
2. **7-test leakage suite** (including random-walk oracle)
3. **Sympy accounting proof** (algebraic identity)
4. **Backtest engine with explicit trading-cost assumptions**
5. **Walk-forward, chronological windows, cross-asset validation**
6. **Frozen data snapshot** with SHA-256 hashes
7. **Full report** (`REPORT.md`)

---

## Quick Start

```bash
git clone https://github.com/darangworks/causal-knn-crypto-strategy.git
cd causal-knn-crypto-strategy
pip install -r requirements.txt

# 7 causal-mechanics tests
pytest tests/test_causal_knn_corrected.py -v

# Accounting equivalence proof
python accounting/sympy_proof.py

# Single backtest
python src/diagnostic_v11_4h_notrail.py

# Walk-forward
python validation/diagnostic_v13_walkforward.py

# Chronological windows
python validation/diagnostic_v14_kfold.py

# Cross-asset
python validation/diagnostic_v15_crossasset.py
```

**Note on dependencies:** Frozen-result reproduction **does not 
require internet access**. `yfinance` is only needed if creating 
a new data snapshot (see `freeze_data.py`).

**Note on `freeze_data.py`:** It is included for transparency about 
how the frozen snapshot was created. It is **not** part of the 
normal reproduction path. To reproduce the reported results, use 
the frozen CSVs in `data/` directly.

---

## Results Summary

| Stage | Result |
|-------|--------|
| Single backtest (BTC 4H) | +$2,000.38 net, 131 trades |
| Walk-Forward | IS −$3,574, OOS +$4,733 |
| Chronological Windows (BTC) | 2/6 positive, total −$2,796 |
| Cross-Asset (BTC/ETH/SOL) | All WEAK |
| Baseline 1H | −$8,806 net |

**The +$2,000 BTC result is not supported by temporal consistency, 
predictive IC, or cross-asset validation.**

---

## Data Freeze

All datasets are frozen with full SHA-256 hashes. See `data/MANIFEST.md`.

| Symbol | Interval | Rows |
|--------|:--------:|:----:|
| BTC-USD | 4h | 4,333 |
| ETH-USD | 4h | 4,333 |
| SOL-USD | 4h | 4,333 |
| BTC-USD | 1h | 17,318 |

**Do not re-run `freeze_data.py`** — it would overwrite this snapshot.

---

## AI Disclosure

**Development:** DeepSeek, Qwen, and one additional chat model. 
All were confidently wrong at least once — four significant errors 
documented in `REPORT.md` Appendix C.

**Evaluation:** Three separately prompted AI evaluations 
(ChatGPT, Claude Sonnet 5, Grok). Raw responses in `evaluations/`.

AI can accelerate research, but verification remains necessary.

---

## License

- **Code (derivatives of Zeiierman's indicator):** CC BY-NC-SA 4.0
- **Documentation:** CC BY 4.0
- **Tests and diagnostic tools (original work):** MIT

See `LICENSE` and `LICENSE-MAP.md` for file-by-file details.

---

## Citation

```bibtex
@misc{darang2026causalknn,
  author = {Mohammad Darang},
  title = {Causal Reconstruction and Validation Study of Zeiierman's 
           AI Predictive Flow Indicator as a Trading Strategy},
  year = {2026},
  howpublished = {GitHub repository},
  url = {https://github.com/darangworks/causal-knn-crypto-strategy}
}
```

---

**No robust edge detected. But the methodology to test for edge 
is now more rigorous than when I started.**
