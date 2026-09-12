# Frozen Data Manifest

**Generated:** 2026-09-12T11:25:32.073360+00:00

## Protocol

> No numeric result from pre-freeze runs is assumed to be
> preserved. Any deviation is treated as a finding, not an
> error to be corrected by code modification.

## Datasets

| Symbol | Interval | Rows | First | Last |
|--------|----------|------|-------|------|
| BTC-USD | 4h | 4333 | 2024-09-13 00:00:00 | 2026-09-12 08:00:00 |
| ETH-USD | 4h | 4333 | 2024-09-13 00:00:00 | 2026-09-12 08:00:00 |
| SOL-USD | 4h | 4333 | 2024-09-13 00:00:00 | 2026-09-12 08:00:00 |
| BTC-USD | 1h | 17318 | 2024-09-13 00:00:00 | 2026-09-12 11:00:00 |

## Full SHA-256

### BTC-USD 4h
- **Path:** `data/BTC_USD_4h_frozen.csv`
- **Rows:** 4333
- **First:** 2024-09-13 00:00:00+00:00
- **Last:** 2026-09-12 08:00:00+00:00
- **Downloaded:** 2026-09-12T11:25:24.891961+00:00
- **SHA-256:** `f61532d5919b9e565018646a480b085aadc85b4ea98284c5c11ab4804b732bf7`

### ETH-USD 4h
- **Path:** `data/ETH_USD_4h_frozen.csv`
- **Rows:** 4333
- **First:** 2024-09-13 00:00:00+00:00
- **Last:** 2026-09-12 08:00:00+00:00
- **Downloaded:** 2026-09-12T11:25:26.636822+00:00
- **SHA-256:** `f955121962d054eebbdb29ac9d9237d12219d8a0874d06a278c3f6a81af80d4a`

### SOL-USD 4h
- **Path:** `data/SOL_USD_4h_frozen.csv`
- **Rows:** 4333
- **First:** 2024-09-13 00:00:00+00:00
- **Last:** 2026-09-12 08:00:00+00:00
- **Downloaded:** 2026-09-12T11:25:28.485177+00:00
- **SHA-256:** `272cdb34c47ecfa17df4bcb5ef77c4dd7515be333826e73857c819113dac2d88`

### BTC-USD 1h
- **Path:** `data/BTC_USD_1h_frozen.csv`
- **Rows:** 17318
- **First:** 2024-09-13 00:00:00+00:00
- **Last:** 2026-09-12 11:00:00+00:00
- **Downloaded:** 2026-09-12T11:25:32.072790+00:00
- **SHA-256:** `5df44197c7c0888c4da0add0cdc223f6a52650ce085b8a99e681d9f4caefd307`

## Data Contract

1. No strategy/feature/parameter change based on frozen results.
2. Any change → Frozen v2 (new directory), not modification of v1.
3. **Do not re-run `freeze_data.py`.** It would overwrite v1.
