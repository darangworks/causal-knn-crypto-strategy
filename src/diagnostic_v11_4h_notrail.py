# =====================================================================
# diagnostic_v11_4h_notrail.py
# =====================================================================
# Purpose: Best-configuration backtest
# Config:  4H timeframe, MTF on, kNN on, trailing disabled
# Date:    2026-09-11
# Data:    data/BTC_USD_4h_frozen.csv (frozen snapshot)
#
# Expected behavior:
#   - ~132 trades on BTC 4H
#   - Net PnL ≈ +$2,000 (full cost)
#   - IC ≈ −0.028
#   - Identity check: ideal_gross - total_cost == net_pnl
#
# Note: Cross-check reference (BASELINE_FINAL_EQUITY) is for 1H
# baseline and does not apply to this 4H configuration.
# =====================================================================

import numpy as np
import pandas as pd
import math
from scipy import stats


# =====================================================================
# CONFIGURATION
# =====================================================================
SYMBOL = "BTC-USD"
TIMEFRAME = "4h"
INITIAL_CAPITAL = 100_000.0
POSITION_PCT = 0.10
COMMISSION = 0.0005
SLIPPAGE = 0.0002

PATTERN_LEN = 10
MEMORY_SIZE = 80
K_NEIGHBORS = 5
AHEAD = 2
PRED_SMOOTH = 4
MIN_PRED_ATR = 0.20

USE_MTF = True
HTF_TIMEFRAME = "4h"
HTF_EMA_LEN = 50
USE_VOLATILITY = True
ATR_LEN = 14
MIN_ATR_PCT = 0.25
BB_LEN = 20
BB_MULT = 2.0
MIN_BB_WIDTH_PCT = 1.0
USE_VOLUME = True
VOLUME_LEN = 20
VOLUME_MULT = 1.1
USE_ADX = True
ADX_LEN = 14
MIN_ADX = 18.0
STOP_ATR = 2.0
TP_ATR = 3.5
TRAIL_ATR = 999.0


# =====================================================================
# DATA LOADING
# =====================================================================
def wilder(s, p):
    return s.ewm(alpha=1.0 / p, adjust=False, min_periods=p).mean()


def load_data():
    print("Loading BTC-USD 4H from frozen CSV...")
    df = pd.read_csv("data/BTC_USD_4h_frozen.csv",
                     index_col=0, parse_dates=True)

    # ---- Integrity guards (fail-fast) ----
    assert isinstance(df.index, pd.DatetimeIndex), "Index is not datetime"
    assert df.index.tz is not None, "Index has no timezone"
    assert str(df.index.tz) == "UTC", f"TZ is {df.index.tz}, expected UTC"
    assert df.index.is_monotonic_increasing, "Index not sorted"
    assert not df.index.has_duplicates, "Duplicate timestamps"
    assert list(df.columns) == ["Open", "High", "Low", "Close", "Volume"]

    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    print(f"Bars: {len(df)}")
    print(f"  First: {df.index[0]}")
    print(f"  Last:  {df.index[-1]}")

    # ATR
    prev = df["Close"].shift(1)
    tr = pd.concat([df["High"] - df["Low"],
                    (df["High"] - prev).abs(),
                    (df["Low"] - prev).abs()], axis=1).max(axis=1)
    df["ATR"] = wilder(tr, ATR_LEN)
    df["ATR_PCT"] = np.where(df["Close"] > 0,
                              df["ATR"] / df["Close"] * 100.0, np.nan)

    # EMAs
    df["EMA_FAST"] = df["Close"].ewm(span=10, adjust=False).mean()
    df["EMA_SLOW"] = df["Close"].ewm(span=30, adjust=False).mean()

    # RSI
    d = df["Close"].diff()
    g = d.clip(lower=0.0)
    l = -d.clip(upper=0.0)
    ag = wilder(g, 14)
    al = wilder(l, 14)
    rs = ag / al.replace(0.0, np.nan)
    df["RSI"] = (100.0 - 100.0 / (1.0 + rs)).fillna(50.0)

    # Bollinger Width
    bb_b = df["Close"].rolling(BB_LEN).mean()
    bb_s = df["Close"].rolling(BB_LEN).std(ddof=1)
    df["BB_WIDTH_PCT"] = np.where(bb_b > 0,
        (2.0 * BB_MULT * bb_s / bb_b) * 100.0, np.nan)

    # Volume
    df["VOL_SMA"] = df["Volume"].rolling(VOLUME_LEN).mean()
    df["VOL_CONF"] = (df["Volume"].notna() & df["VOL_SMA"].notna()
                      & (df["Volume"] > df["VOL_SMA"] * VOLUME_MULT))

    # ADX
    up = df["High"].diff()
    dn = -df["Low"].diff()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=df.index)
    mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=df.index)
    ps = wilder(pdm, ADX_LEN)
    ms = wilder(mdm, ADX_LEN)
    as_ = df["ATR"].replace(0.0, np.nan)
    dip = 100.0 * ps / as_
    dim = 100.0 * ms / as_
    dis = (dip + dim).replace(0.0, np.nan)
    dx = 100.0 * (dip - dim).abs() / dis
    df["ADX"] = wilder(dx.fillna(0.0), ADX_LEN)

    # HTF EMA confirmed
    htf_c = df["Close"].resample(HTF_TIMEFRAME).last()
    htf_e = htf_c.ewm(span=HTF_EMA_LEN, adjust=False).mean()
    df["HTF_EMA"] = htf_e.shift(1).reindex(df.index, method="ffill")
    df["HTF_BULL"] = df["Close"] > df["HTF_EMA"]
    df["HTF_BEAR"] = df["Close"] < df["HTF_EMA"]

    # Features
    vn = np.maximum(df["ATR"] / df["Close"], 1e-6)
    f1 = np.log(df["Close"] / df["Close"].shift(1)) / vn
    f2 = (df["Close"] - df["Close"].shift(5)) / df["ATR"]
    f3 = (df["RSI"] - 50.0) / 50.0
    f4 = (df["EMA_FAST"] - df["EMA_SLOW"]) / df["ATR"]
    for c, s in [("f1", f1), ("f2", f2), ("f3", f3), ("f4", f4)]:
        df[c] = np.clip(s.replace([np.inf, -np.inf], 0.0).fillna(0.0),
                        -5.0, 5.0)
    return df


# =====================================================================
# BLOCK LENGTH ESTIMATION FROM ACF
# =====================================================================
def estimate_block_length(preds, max_lag=100, z=1.96):
    s = np.asarray(preds, dtype=float)
    s = s[np.isfinite(s)]
    if len(s) < max_lag * 2:
        return max(AHEAD, PATTERN_LEN + PRED_SMOOTH)
    s = s - s.mean()
    if s.var() < 1e-12:
        return max(AHEAD, PATTERN_LEN + PRED_SMOOTH)
    n = len(s)
    acf = np.correlate(s, s, mode='full')[n - 1:] / (
        s.var() * np.arange(n, 0, -1))
    thr = z / np.sqrt(n)
    for lag in range(1, max_lag):
        if abs(acf[lag]) < thr:
            return max(lag * 2, AHEAD)
    return max_lag


# =====================================================================
# BACKTEST ENGINE — strict chronology, gap-aware
# =====================================================================
def run_engine(df, comm, slip):
    o = df["Open"].values.astype(float)
    h = df["High"].values.astype(float)
    lo = df["Low"].values.astype(float)
    c = df["Close"].values.astype(float)
    a = df["ATR"].values.astype(float)
    ap = df["ATR_PCT"].values.astype(float)
    f1 = df["f1"].values.astype(float)
    f2 = df["f2"].values.astype(float)
    f3 = df["f3"].values.astype(float)
    f4 = df["f4"].values.astype(float)
    hb = df["HTF_BULL"].fillna(False).astype(bool).values
    hbe = df["HTF_BEAR"].fillna(False).astype(bool).values
    bw = df["BB_WIDTH_PCT"].values.astype(float)
    ax = df["ADX"].values.astype(float)
    vc = df["VOL_CONF"].fillna(False).astype(bool).values

    n = len(df)
    X = np.zeros((MEMORY_SIZE, PATTERN_LEN * 4))
    Y = np.zeros(MEMORY_SIZE)
    head = 0
    count = 0
    pred_ema = None
    alpha = 2.0 / (PRED_SMOOTH + 1.0) if PRED_SMOOTH > 1 else 1.0

    equity = INITIAL_CAPITAL
    pos = 0
    qty = 0.0
    ep = 0.0
    eb = 0.0
    eb_i = None
    ecm = 0.0
    istop = 0.0
    tstop = 0.0
    tgt = 0.0
    pend = 0
    patr = np.nan

    curve = np.zeros(n)
    trades = []
    bars = 0
    pre = []

    req = max(350, PATTERN_LEN + AHEAD + 50, HTF_EMA_LEN * 4 + 50)

    def do_exit(i, xp, reason):
        nonlocal equity, pos, qty, ep, eb, eb_i, ecm, istop, tstop, tgt
        if pos == 0 or qty <= 0:
            return

        if pos == 1:
            fill = xp * (1.0 - slip)
            gr = (fill - ep) * qty
        else:
            fill = xp * (1.0 + slip)
            gr = (ep - fill) * qty
        xc = fill * qty * comm
        equity += gr - xc

        ig = (xp - eb) * qty if pos == 1 else (eb - xp) * qty
        es = abs(ep - eb) * qty
        xs = abs(fill - xp) * qty
        tc = es + xs + ecm + xc
        net = ig - tc

        trades.append({
            "signal_bar": (eb_i - 1) if eb_i is not None else "",
            "entry_bar": eb_i if eb_i is not None else "",
            "exit_bar": i,
            "direction": "long" if pos == 1 else "short",
            "ideal_entry": eb,
            "actual_entry": ep,
            "ideal_exit": xp,
            "actual_exit": fill,
            "qty": qty,
            "ideal_gross": ig,
            "entry_slip": es,
            "exit_slip": xs,
            "entry_comm": ecm,
            "exit_comm": xc,
            "total_cost": tc,
            "net_pnl": net,
            "exit_reason": reason,
        })

        pos = 0
        qty = 0.0
        ep = 0.0
        eb = 0.0
        eb_i = None
        ecm = 0.0
        istop = 0.0
        tstop = 0.0
        tgt = 0.0

    for i in range(n):
        # STEP A: Execute pending signal at Open[i]
        if pend != 0 and i > 0:
            if pos != 0 and pos != pend:
                do_exit(i, o[i], "signal_reverse")
            if pos == 0:
                d = pend
                ea = patr if np.isfinite(patr) else a[i]
                if np.isfinite(ea) and ea > 0 and equity > 0:
                    eb = o[i]
                    ep = eb * (1.0 + slip) if d == 1 else eb * (1.0 - slip)
                    qty = (equity * POSITION_PCT) / ep
                    eb_i = i
                    ecm = ep * qty * comm
                    equity -= ecm
                    if d == 1:
                        istop = ep - STOP_ATR * ea
                        tgt = ep + TP_ATR * ea
                    else:
                        istop = ep + STOP_ATR * ea
                        tgt = ep - TP_ATR * ea
                    tstop = istop
                    pos = d
            pend = 0
            patr = np.nan

        # STEP B: Intrabar stop/TP check
        if pos != 0:
            if pos == 1:
                es = max(istop, tstop)
                if o[i] <= es:
                    do_exit(i, o[i], "gap_stop")
                elif lo[i] <= es:
                    do_exit(i, es, "stop")
                elif o[i] >= tgt:
                    do_exit(i, o[i], "gap_tp")
                elif h[i] >= tgt:
                    do_exit(i, tgt, "tp")
            else:
                es = min(istop, tstop)
                if o[i] >= es:
                    do_exit(i, o[i], "gap_stop")
                elif h[i] >= es:
                    do_exit(i, es, "stop")
                elif o[i] <= tgt:
                    do_exit(i, o[i], "gap_tp")
                elif lo[i] <= tgt:
                    do_exit(i, tgt, "tp")

        # STEP C: Update trailing stop at close
        if pos != 0 and np.isfinite(a[i]) and a[i] > 0:
            if pos == 1:
                tstop = max(tstop, c[i] - TRAIL_ATR * a[i])
            else:
                tstop = min(tstop, c[i] + TRAIL_ATR * a[i])

        if pos != 0:
            bars += 1

        # STEP D: Causal kNN update at close
        rp = None
        if i >= req:
            te = i - AHEAD
            if te >= PATTERN_LEN - 1:
                s0 = te - PATTERN_LEN + 1
                vec = np.concatenate([f1[s0:te + 1], f2[s0:te + 1],
                                       f3[s0:te + 1], f4[s0:te + 1]])
                if c[i] > 0 and c[te] > 0:
                    lab = math.log(c[i] / c[te])
                    idx = head % MEMORY_SIZE
                    X[idx] = vec
                    Y[idx] = lab
                    head += 1
                    count = min(count + 1, MEMORY_SIZE)

            if i >= PATTERN_LEN - 1:
                s0 = i - PATTERN_LEN + 1
                q = np.concatenate([f1[s0:i + 1], f2[s0:i + 1],
                                     f3[s0:i + 1], f4[s0:i + 1]])
                if count >= K_NEIGHBORS:
                    vX = X[:count] if count < MEMORY_SIZE else X
                    vY = Y[:count] if count < MEMORY_SIZE else Y
                    ds = np.linalg.norm(vX - q, axis=1)
                    if K_NEIGHBORS < len(ds):
                        t = np.argpartition(ds, K_NEIGHBORS - 1)[:K_NEIGHBORS]
                    else:
                        t = np.argsort(ds)
                    dt = ds[t]
                    yt = vY[t]
                    w = 1.0 / (dt + 1e-6)
                    ws = w.sum()
                    if ws > 0:
                        rp = float((w * yt).sum() / ws)

            if rp is not None:
                if pred_ema is None:
                    pred_ema = rp
                else:
                    pred_ema = alpha * rp + (1 - alpha) * pred_ema

        if (pred_ema is not None and np.isfinite(ap[i]) and ap[i] > 0
                and i + AHEAD < n):
            fr = math.log(c[i + AHEAD] / c[i]) if c[i] > 0 else 0.0
            pre.append({
                "bar": i,
                "pred": float(pred_ema),
                "score": float(pred_ema / (ap[i] / 100.0)),
                "fwd_ret": float(fr),
            })

        # STEP E: Generate signal for bar i+1
        if (i < n - 1 and pred_ema is not None
                and np.isfinite(ap[i]) and ap[i] > 0):
            sc = pred_ema / (ap[i] / 100.0)
            vr = (np.isfinite(ap[i]) and np.isfinite(bw[i])
                  and ap[i] >= MIN_ATR_PCT and bw[i] >= MIN_BB_WIDTH_PCT)
            ar = np.isfinite(ax[i]) and ax[i] >= MIN_ADX
            lf = ((not USE_MTF or hb[i])
                  and (not USE_VOLATILITY or vr)
                  and (not USE_VOLUME or vc[i])
                  and (not USE_ADX or ar))
            sf = ((not USE_MTF or hbe[i])
                  and (not USE_VOLATILITY or vr)
                  and (not USE_VOLUME or vc[i])
                  and (not USE_ADX or ar))
            if sc >= MIN_PRED_ATR and lf and pos <= 0:
                pend = 1
                patr = a[i]
            elif sc <= -MIN_PRED_ATR and sf and pos >= 0:
                pend = -1
                patr = a[i]

        # STEP F: Mark-to-market
        unr = 0.0
        if pos == 1:
            unr = (c[i] - ep) * qty
        elif pos == -1:
            unr = (ep - c[i]) * qty
        curve[i] = equity + unr

    if pos != 0:
        do_exit(n - 1, c[-1], "end_of_data")
        curve[-1] = equity

    return curve, trades, bars, pre


# =====================================================================
# REPORTING
# =====================================================================
def report(label, run):
    curve, trades, bars, pre = run
    print(f"\n{'=' * 70}")
    print(f"SCENARIO: {label}")
    print(f"{'=' * 70}")

    if not trades:
        print("No trades.")
        return

    t = pd.DataFrame(trades)
    ig = t["ideal_gross"].sum()
    tc = t["total_cost"].sum()
    net = t["net_pnl"].sum()

    print(f"Total Trades:          {len(t)}")
    print(f"Ideal Gross PnL:       ${ig:>14,.2f}")
    print(f"Total Cost:            ${-tc:>14,.2f}")
    print(f"  Entry Slippage:      ${-t['entry_slip'].sum():>14,.2f}")
    print(f"  Exit Slippage:       ${-t['exit_slip'].sum():>14,.2f}")
    print(f"  Entry Commission:    ${-t['entry_comm'].sum():>14,.2f}")
    print(f"  Exit Commission:     ${-t['exit_comm'].sum():>14,.2f}")
    print(f"Net PnL:               ${net:>14,.2f}")
    print(f"Identity check:        "
          f"{'OK' if abs(ig - tc - net) < 1e-3 else 'FAIL'}")

    wins = t[t["net_pnl"] > 0]["net_pnl"]
    losses = t[t["net_pnl"] <= 0]["net_pnl"]
    wr = 100.0 * len(wins) / len(t)
    pf = wins.sum() / abs(losses.sum()) if losses.sum() != 0 else float("nan")
    print(f"\nWin Rate:              {wr:.2f}%")
    print(f"Net Profit Factor:     {pf:.3f}" if np.isfinite(pf) else "Net PF: n/a")

    if len(pre) > 50:
        p = np.array([r["pred"] for r in pre])
        f = np.array([r["fwd_ret"] for r in pre])
        ic_p = stats.pearsonr(p, f)[0]
        ic_s = stats.spearmanr(p, f)[0]
        da = float(np.mean(np.sign(p) == np.sign(f)))
        bl = estimate_block_length(p)

        print(f"\n--- UNCONDITIONAL IC ---")
        print(f"  N observations:        {len(p)}")
        print(f"  Pearson IC:            {ic_p:+.5f}")
        print(f"  Spearman IC:           {ic_s:+.5f}")
        print(f"  Directional Accuracy:  {da * 100:.2f}%")
        print(f"  ACF block_len (auto):  {bl}")

        q = pd.qcut(p, 5, labels=False, duplicates="drop")
        print(f"\n--- PREDICTION QUINTILES ---")
        means = []
        for k in sorted(np.unique(q)):
            m = q == k
            mr = float(f[m].mean() * 100)
            means.append(mr)
            print(f"  Q{int(k) + 1}: {mr:+.4f}%   (n = {m.sum()})")
        if len(means) == 5:
            print(f"  Q5 - Q1 spread:        {means[4] - means[0]:+.4f}%")
            rank_corr = stats.spearmanr(range(5), means)[0]
            print(f"  Rank corr (Q, mean):   {rank_corr:+.3f}")


# =====================================================================
# MAIN
# =====================================================================
def main():
    df = load_data()

    scenarios = [
        ("ZERO COST", 0.0, 0.0),
        ("COMMISSION ONLY", COMMISSION, 0.0),
        ("SLIPPAGE ONLY", 0.0, SLIPPAGE),
        ("FULL COST", COMMISSION, SLIPPAGE),
    ]

    full_run = None
    for label, c, s in scenarios:
        run = run_engine(df, c, s)
        report(label, run)
        if label == "FULL COST":
            full_run = run


if __name__ == "__main__":
    main()