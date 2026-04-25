# =============================================================
#  optimizer.py  –  Code Optimization Phase
#
#  Machine-Independent:
#    • Constant Folding  – evaluate constant expressions at
#      compile time   e.g.  t1 = 3 + 4  →  t1 = 7
#
#  Machine-Dependent (Peephole):
#    • Remove redundant MOV  e.g.  MOV R0, R0  → deleted
#    • Collapse  MOV then ADD into one instruction (simple demo)
# =============================================================

from __future__ import annotations
import re


# ── Helper: is a string a numeric constant? ───────────────────
def _is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False


def _eval_op(a: str, op: str, b: str) -> str | None:
    """Evaluate binary op on two numeric strings. Returns None if not foldable."""
    try:
        va, vb = float(a), float(b)
        if op == '+':  result = va + vb
        elif op == '-': result = va - vb
        elif op == '*': result = va * vb
        elif op == '/':
            if vb == 0:
                return None
            result = va / vb
        elif op == '<':  result = int(va < vb)
        elif op == '>':  result = int(va > vb)
        elif op == '==': result = int(va == vb)
        elif op == '!=': result = int(va != vb)
        elif op == '<=': result = int(va <= vb)
        elif op == '>=': result = int(va >= vb)
        else: return None
        # Return int string if result is whole number
        return str(int(result)) if result == int(result) else str(result)
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════
#  1.  CONSTANT FOLDING  (machine-independent)
# ═══════════════════════════════════════════════════════════════
# TAC line patterns:
#   "  t1 = 3 + 4"      → binary assignment
#   "  t1 = 7"          → simple assignment
BINARY_ASSIGN = re.compile(
    r'^\s*(\w+)\s*=\s*(\S+)\s*([+\-*/]|==|!=|<=|>=|<|>)\s*(\S+)\s*$'
)
SIMPLE_ASSIGN = re.compile(r'^\s*(\w+)\s*=\s*(\S+)\s*$')


def constant_folding(tac_lines: list[str]) -> list[str]:
    """
    Perform constant folding on TAC.
    Returns new TAC list with constants pre-computed.
    """
    # Map: temp → constant value (if known)
    const_map: dict[str, str] = {}
    optimised: list[str]      = []
    changes = 0

    for line in tac_lines:
        m = BINARY_ASSIGN.match(line)
        if m:
            res, a1, op, a2 = m.group(1), m.group(2), m.group(3), m.group(4)
            # Substitute known constants
            a1 = const_map.get(a1, a1)
            a2 = const_map.get(a2, a2)
            folded = _eval_op(a1, op, a2) if _is_number(a1) and _is_number(a2) else None
            if folded is not None:
                new_line = f"  {res} = {folded}   # folded: {a1}{op}{a2}"
                const_map[res] = folded
                optimised.append(new_line)
                changes += 1
            else:
                optimised.append(line)
        else:
            m2 = SIMPLE_ASSIGN.match(line)
            if m2:
                res, val = m2.group(1), m2.group(2)
                val = const_map.get(val, val)
                if _is_number(val):
                    const_map[res] = val
            optimised.append(line)

    return optimised, changes


# ═══════════════════════════════════════════════════════════════
#  2.  PEEPHOLE OPTIMISATION  (machine-dependent)
# ═══════════════════════════════════════════════════════════════
REDUNDANT_MOV = re.compile(r'^\s*MOV\s+(\w+)\s*,\s*\1\s*$')   # MOV R0, R0


def peephole(asm_lines: list[str]) -> list[str]:
    """
    Simple peephole pass on assembly-like output.
    Removes:
      • MOV Rx, Rx   (move register to itself)
      • Consecutive duplicate lines
    """
    result  = []
    changes = 0
    prev    = None

    for line in asm_lines:
        # Remove MOV Rx, Rx
        if REDUNDANT_MOV.match(line):
            changes += 1
            continue
        # Remove consecutive duplicate instructions
        if line == prev:
            changes += 1
            continue
        result.append(line)
        prev = line

    return result, changes


# ── Public entry point ────────────────────────────────────────
def run_optimizer(tac_lines: list[str], asm_lines: list[str]) \
        -> tuple[list[str], list[str]]:

    print("\n" + "=" * 55)
    print("  PHASE 5 – CODE OPTIMIZATION")
    print("=" * 55)

    # ── Constant folding ──────────────────────────────────────
    print("\n  ── Machine-Independent: Constant Folding ──")
    opt_tac, cf_changes = constant_folding(tac_lines)
    if cf_changes:
        for line in opt_tac:
            print(line)
        print(f"\n  [{cf_changes} constant(s) folded]")
    else:
        print("  No constants to fold in this program.")
        opt_tac = tac_lines

    # ── Peephole ──────────────────────────────────────────────
    print("\n  ── Machine-Dependent: Peephole Optimization ──")
    opt_asm, ph_changes = peephole(asm_lines)
    if ph_changes:
        print(f"  Removed {ph_changes} redundant instruction(s).")
    else:
        print("  No redundant instructions found.")
    for line in opt_asm:
        print(line)

    print("=" * 55)
    return opt_tac, opt_asm
