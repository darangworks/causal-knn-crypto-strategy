
# Reproducibility Guide

Step-by-step instructions to reproduce every result in this repository.

---

## Requirements

- Python 3.10+
- ~500 MB disk space
- No internet access required for frozen-result reproduction

```bash
pip install -r requirements.txt
```

---

## Step 1 — Verify 7 Causal-Mechanics Tests

```bash
pytest tests/test_causal_knn_corrected.py -v
```

**Expected output:** 7 passed.

---

## Step 2 — Verify Sympy Accounting Proof

```bash
python accounting/sympy_proof.py
```

**Expected output:** `Difference = 0` and `Identity confirmed`.

---

## Step 3 — Frozen-Result Reproduction

For reproducing the reported results, **no internet access is
required**. The frozen CSVs in `data/` are the canonical reference.

**Do not run `freeze_data.py` for reproduction.** It is included
only to document how the frozen snapshot was created.

To verify the frozen data is intact, compare SHA-256 hashes in
`data/MANIFEST.md`:

```bash
python -c "import hashlib; print(hashlib.sha256(open('data/BTC_USD_4h_frozen.csv','rb').read()).hexdigest())"
```

---

## Step 3b — Initial Dataset Creation (Optional)

If you need to re-create the frozen snapshot from scratch (e.g., for
a **Frozen v2** with a different time window), `freeze_data.py` can
be used. This is **not part of normal reproduction**.

**Warning:** Running this will overwrite the current frozen snapshot.
If creating a new version, first back up the existing `data/` directory.

```bash
# Optional: only if creating a new snapshot
python freeze_data.py
```

---

## Step 4 — Reproduce All Results

```bash
python src/diagnostic_v11_4h_notrail.py
python validation/diagnostic_v13_walkforward.py
python validation/diagnostic_v14_kfold.py
python validation/diagnostic_v15_crossasset.py
python src/run_local_baseline.py
```

---

## Expected Results (Frozen Snapshot)

| File | Expected |
|------|----------|
| pytest | 7 passed |
| sympy | Difference = 0 |
| v11 (BTC 4H) | 131 trades, Net +$2,000.38, IC −0.028 |
| Walk-Forward IS | 58 trades, −$3,573.68 |
| Walk-Forward OOS | 57 trades, +$4,733.23 |
| BTC Windows | 2/6 positive, total −$2,796 |
| ETH Windows | 3/6 positive, total −$834 |
| SOL Windows | 2/6 positive, total −$4,192 |
| Baseline 1H | 628 trades, −$8,805.86 |

---

## Tolerance for Reproduction

| Metric | Tolerance |
|--------|-----------|
| Trade count | exact |
| Entry/exit timestamps | exact |
| Signal sequence | exact |
| Net PnL | rtol=1e-10, atol=1e-8 |
| IC | rtol=1e-6, atol=1e-8 |
| Equity curve | rtol=1e-8, atol=1e-6 |
| Sympy proof | exact |

If your run differs by more than these tolerances, please open an issue.

---

## Data Integrity

Each frozen CSV has a SHA-256 hash recorded in `data/MANIFEST.md`.
To verify:

```bash
python -c "import hashlib; print(hashlib.sha256(open('data/BTC_USD_4h_frozen.csv','rb').read()).hexdigest())"
```

Compare to the hash in `data/MANIFEST.md`.

**Note:** The frozen CSV is the canonical serialized snapshot used
for all subsequent experiments.

---

## Data Contract

**Version:** v1
**Frozen:** 2026-09-12

1. No changes to strategy, features, thresholds, kNN parameters,
   filters, or execution logic may be made based solely on the
   frozen results.
2. Any required change must be a new version (`Frozen v2`), not a
   modification of v1.
3. **Do not re-run `freeze_data.py`.** It would overwrite this snapshot.
