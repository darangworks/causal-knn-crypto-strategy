"""
sympy_proof.py

Symbolic equivalence proof for the two accounting formulations used
in the backtest engine.

Scope:
    This proof establishes algebraic equivalence between two specified
    accounting formulations:

        (A) Baseline formulation:
            - Fill prices include slippage.
            - Entry commission deducted immediately from equity.
            - Exit commission deducted at exit.

        (B) Report formulation (v2):
            - Ideal gross computed from ideal prices.
            - Slippage and commissions computed separately.
            - Net = ideal_gross - entry_slip - exit_slip
                    - entry_comm - exit_comm.

    This proof is NOT a proof of correctness of the entire backtesting
    engine, position sizing, execution logic, or commission application.

Usage:
    python accounting/sympy_proof.py

Expected output:
    E_final_baseline - E_final_v2 = 0
    Identity confirmed.
"""

import sympy as sp


def prove_accounting_equivalence():
    # ─────────────────────────────────────────────────────────────
    # Symbolic variables
    # ─────────────────────────────────────────────────────────────
    E0 = sp.Symbol("E0", real=True)                     # initial equity
    qty = sp.Symbol("qty", positive=True)               # position size
    entry_ideal = sp.Symbol("entry_ideal", positive=True)
    exit_ideal = sp.Symbol("exit_ideal", positive=True)
    comm = sp.Symbol("comm", positive=True)             # commission rate
    slip = sp.Symbol("slip", positive=True)             # slippage rate

    # ─────────────────────────────────────────────────────────────
    # (A) Baseline formulation
    # ─────────────────────────────────────────────────────────────
    fill_entry = entry_ideal * (1 + slip)
    fill_exit = exit_ideal * (1 - slip)

    # Entry commission deducted immediately
    entry_comm_b = fill_entry * qty * comm
    E_entry = E0 - entry_comm_b

    # Gross realized at exit (based on fills)
    gross_realized = (fill_exit - fill_entry) * qty
    exit_comm_b = fill_exit * qty * comm

    E_final_baseline = E_entry + gross_realized - exit_comm_b

    # ─────────────────────────────────────────────────────────────
    # (B) Report formulation (v2)
    # ─────────────────────────────────────────────────────────────
    # Ideal gross (no slippage, no commission)
    ideal_gross = (exit_ideal - entry_ideal) * qty

    # Slippage components
    entry_slip_total = (fill_entry - entry_ideal) * qty
    exit_slip_total = (exit_ideal - fill_exit) * qty

    # Commission components (based on fills)
    entry_comm_v2 = fill_entry * qty * comm
    exit_comm_v2 = fill_exit * qty * comm

    E_final_v2 = (
        E0
        + ideal_gross
        - entry_slip_total
        - exit_slip_total
        - entry_comm_v2
        - exit_comm_v2
    )

    # ─────────────────────────────────────────────────────────────
    # Compute difference symbolically
    # ─────────────────────────────────────────────────────────────
    difference = sp.simplify(E_final_baseline - E_final_v2)

    print("=" * 60)
    print("SYMBOLIC ACCOUNTING EQUIVALENCE PROOF")
    print("=" * 60)
    print()
    print("E_final_baseline =", sp.simplify(E_final_baseline))
    print()
    print("E_final_v2       =", sp.simplify(E_final_v2))
    print()
    print("Difference       =", difference)
    print()

    # ─────────────────────────────────────────────────────────────
    # Assert identity
    # ─────────────────────────────────────────────────────────────
    assert difference == 0, (
        "IDENTITY FAILED — the two accounting formulations are NOT "
        "algebraically equivalent."
    )

    print("=" * 60)
    print("RESULT")
    print("=" * 60)
    print("Identity confirmed:")
    print("    E_final_baseline - E_final_v2 = 0")
    print()
    print("This holds for ALL possible values of:")
    print("    entry_ideal, exit_ideal, qty, comm, slip")
    print()
    print("Scope:")
    print("    This proof establishes ALGEBRAIC EQUIVALENCE between the")
    print("    two specified accounting formulations. It does NOT prove")
    print("    correctness of the entire backtesting engine, position")
    print("    sizing, execution logic, or commission application.")
    print("=" * 60)


if __name__ == "__main__":
    prove_accounting_equivalence()
