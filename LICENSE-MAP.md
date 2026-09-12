# License Map

Explicit license assignment for every file in this repository.

**Reason:** This project is a derivative of "AI Predictive Flow" by
Zeiierman (CC BY-NC-SA 4.0). The distinction between original work,
derivative work, and third-party content must be explicit.

---

## 1. Derivative of the Original Indicator — CC BY-NC-SA 4.0

| File | Reason |
|------|--------|
| `src/diagnostic_v11_4h_notrail.py` | Implements causal kNN engine and features derived from the indicator |
| `validation/diagnostic_v13_walkforward.py` | Same kNN engine |
| `validation/diagnostic_v14_kfold.py` | Same kNN engine |
| `validation/diagnostic_v15_crossasset.py` | Same kNN engine |
| `src/run_local_baseline.py` | Same kNN engine (1H configuration) |
| `tests/test_causal_knn_corrected.py` | Reference implementation of the causal kNN logic |

**Commercial use:** Not permitted. Any permission for uses outside
the license terms must be obtained from the applicable rights holder(s).

---

## 2. Original Work — Diagnostic Tools — MIT

| File | Reason |
|------|--------|
| `accounting/sympy_proof.py` | Pure algebra; no indicator logic |
| `freeze_data.py` | Data download utility; no indicator logic |

**Commercial use:** Permitted under MIT.

---

## 3. Original Work — Documentation — CC BY 4.0

| File | Reason |
|------|--------|
| `REPORT.md` | Original research documentation |
| `README.md` | Original documentation |
| `REPRODUCIBILITY.md` | Original documentation |
| `LICENSE-MAP.md` | Original documentation (this file) |
| `research_log/configurations.md` | Original research log |
| `evaluations/*.md` | Preserved responses from independent evaluators |

**Commercial use:** Permitted under CC BY 4.0.

---

## 4. Frozen Market Data — Third-Party Data

Files under `data/` are frozen market-data snapshots obtained from
Yahoo Finance.

**This project does not claim copyright ownership over the underlying
third-party market data and does not relicense it under CC BY 4.0.**

Included solely to support reproducibility. Users are responsible
for ensuring their use complies with the applicable Yahoo Finance
terms.

**Commercial use:** Subject to the data provider's terms.

---

## 5. Frozen Research Results — CC BY 4.0 (project-authored)

Files under `results/` are the project's own output files.

**License:** CC BY 4.0 (project-authored content only).

**Caveat:** If any result file embeds raw third-party data values,
those specific elements are not relicensed. The analysis, aggregation,
and commentary are the project's original work.

**Commercial use:** Permitted for project-authored content under
CC BY 4.0, subject to the caveat above.

---

## Summary Table

| Category | License / Terms | Commercial use |
|----------|-----------------|:--------------:|
| Derivative indicator logic | CC BY-NC-SA 4.0 | ❌ |
| Original diagnostic tools | MIT | ✅ |
| Original documentation | CC BY 4.0 | ✅ |
| Third-party market data | Provider terms | ⚠️ |
| Frozen research results | CC BY 4.0* | ⚠️ |

\* Project-authored content only.

---

## Attribution to Zeiierman

This work is a derivative of "AI Predictive Flow" by Zeiierman
(https://www.tradingview.com/script/qaaxkW1P-AI-Predictive-Flow-Zeiierman/),
licensed under CC BY-NC-SA 4.0.

**Changes made:**
- Reconstructed target variable to eliminate backward-looking bias
- Removed self-contamination of training set
- Converted Pine Script to Python for local backtesting
- Added verification pipeline (7 leakage tests, sympy accounting proof)
- Added walk-forward, chronological windows, and cross-asset validation
- Frozen data snapshot with SHA-256 hashes

**License of derivative files:** CC BY-NC-SA 4.0

---

*This license map is provided for transparency and is not legal
advice. Users should consult their own legal counsel regarding
compliance.*