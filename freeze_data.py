# freeze_data.py
import os
import hashlib
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf


def sha256_full(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def freeze(symbol, interval, path):
    print(f"Downloading {symbol} {interval}...")

    df = yf.download(symbol, interval=interval, period="730d",
                     auto_adjust=False, progress=False)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()

    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index.tz is not None
    assert str(df.index.tz) == "UTC"
    assert df.index.is_monotonic_increasing
    assert not df.index.has_duplicates
    assert list(df.columns) == ["Open", "High", "Low", "Close", "Volume"]

    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Canonical serialized snapshot (not raw byte-for-byte)
    df.to_csv(path, date_format="%Y-%m-%d %H:%M:%S%z")

    sha = sha256_full(path)
    meta = {
        "symbol": symbol,
        "interval": interval,
        "rows": len(df),
        "first_timestamp": str(df.index[0]),
        "last_timestamp": str(df.index[-1]),
        "columns": list(df.columns),
        "download_timestamp": datetime.now(timezone.utc).isoformat(),
        "sha256": sha,
        "path": path,
    }

    print(f"  Saved: {path}")
    print(f"  Rows:  {len(df)}")
    print(f"  First: {df.index[0]}")
    print(f"  Last:  {df.index[-1]}")
    print(f"  SHA256: {sha}\n")
    return meta


def write_manifest(metas, path="data/MANIFEST.md"):
    lines = [
        "# Frozen Data Manifest",
        "",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Protocol",
        "",
        "> No numeric result from pre-freeze runs is assumed to be",
        "> preserved. Any deviation is treated as a finding, not an",
        "> error to be corrected by code modification.",
        "",
        "## Datasets",
        "",
        "| Symbol | Interval | Rows | First | Last |",
        "|--------|----------|------|-------|------|",
    ]
    for m in metas:
        lines.append(
            f"| {m['symbol']} | {m['interval']} | {m['rows']} | "
            f"{m['first_timestamp'][:19]} | {m['last_timestamp'][:19]} |"
        )

    lines += ["", "## Full SHA-256", ""]
    for m in metas:
        lines += [
            f"### {m['symbol']} {m['interval']}",
            f"- **Path:** `{m['path']}`",
            f"- **Rows:** {m['rows']}",
            f"- **First:** {m['first_timestamp']}",
            f"- **Last:** {m['last_timestamp']}",
            f"- **Downloaded:** {m['download_timestamp']}",
            f"- **SHA-256:** `{m['sha256']}`",
            "",
        ]

    lines += [
        "## Data Contract",
        "",
        "1. No strategy/feature/parameter change based on frozen results.",
        "2. Any change → Frozen v2 (new directory), not modification of v1.",
        "3. **Do not re-run `freeze_data.py`.** It would overwrite v1.",
        "",
    ]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Manifest written to {path}")


def main():
    print("=" * 70)
    print("FREEZING DATA — run ONCE")
    print("=" * 70 + "\n")

    metas = [
        freeze("BTC-USD", "4h", "data/BTC_USD_4h_frozen.csv"),
        freeze("ETH-USD", "4h", "data/ETH_USD_4h_frozen.csv"),
        freeze("SOL-USD", "4h", "data/SOL_USD_4h_frozen.csv"),
        freeze("BTC-USD", "1h", "data/BTC_USD_1h_frozen.csv"),
    ]
    write_manifest(metas)
    print("=" * 70)
    print("Data frozen. DO NOT re-run this script.")
    print("=" * 70)


if __name__ == "__main__":
    main()