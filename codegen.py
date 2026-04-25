# =============================================================
#  codegen.py  –  Target Code Generation Phase
#  Translates Three Address Code → simple assembly-like code
#
#  Register model: R0–R4 (simple round-robin allocator)
#  Instructions used: MOV, ADD, SUB, MUL, DIV, CMP, JMP,
#                     JZ (jump if zero), PRINT, LABEL
# =============================================================

from __future__ import annotations
import re

BINARY_ASSIGN = re.compile(
    r'^\s*(\w+)\s*=\s*(\S+)\s*([+\-*/]|==|!=|<=|>=|<|>)\s*(\S+)\s*$'
)
SIMPLE_ASSIGN  = re.compile(r'^\s*(\w+)\s*=\s*(\S+)\s*$')
IF_FALSE       = re.compile(r'^\s*if_false\s+(\S+)\s+goto\s+(\S+)\s*$')
GOTO_PAT       = re.compile(r'^\s*goto\s+(\S+)\s*$')
LABEL_PAT      = re.compile(r'^(\w+):$')
PRINT_PAT      = re.compile(r'^\s*print\s+(\S+)\s*$')


class RegisterAllocator:
    """Trivially allocates the next free register (round-robin)."""
    REGS = ['R0', 'R1', 'R2', 'R3', 'R4']

    def __init__(self):
        self._map: dict[str, str] = {}
        self._idx = 0

    def get(self, name: str) -> str:
        if name not in self._map:
            reg = self.REGS[self._idx % len(self.REGS)]
            self._map[name] = reg
            self._idx += 1
        return self._map[name]


OP_TO_INSTR = {
    '+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV',
    '<': 'CMP', '>': 'CMP', '==': 'CMP', '!=': 'CMP',
    '<=': 'CMP', '>=': 'CMP',
}


def _is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def generate_code(tac_lines: list[str]) -> list[str]:
    """Translate TAC lines to assembly-like instructions."""
    alloc = RegisterAllocator()
    asm   = []

    for line in tac_lines:
        # ── Label ─────────────────────────────────────────────
        m = LABEL_PAT.match(line)
        if m:
            asm.append(f"{m.group(1)}:")
            continue

        # ── goto ──────────────────────────────────────────────
        m = GOTO_PAT.match(line)
        if m:
            asm.append(f"  JMP  {m.group(1)}")
            continue

        # ── if_false cond goto label ──────────────────────────
        m = IF_FALSE.match(line)
        if m:
            cond_var, lbl = m.group(1), m.group(2)
            reg = alloc.get(cond_var)
            asm.append(f"  CMP  {reg}, 0")
            asm.append(f"  JZ   {lbl}")
            continue

        # ── print ─────────────────────────────────────────────
        m = PRINT_PAT.match(line)
        if m:
            val = m.group(1)
            reg = alloc.get(val) if not _is_number(val) else val
            asm.append(f"  PRINT {reg}")
            continue

        # ── binary:  result = a op b ──────────────────────────
        m = BINARY_ASSIGN.match(line)
        if m:
            res, a1, op, a2 = m.group(1), m.group(2), m.group(3), m.group(4)
            r_res = alloc.get(res)
            src1  = alloc.get(a1) if not _is_number(a1) else f"#{a1}"
            src2  = alloc.get(a2) if not _is_number(a2) else f"#{a2}"
            instr = OP_TO_INSTR.get(op, 'OP')
            asm.append(f"  MOV  {r_res}, {src1}")
            asm.append(f"  {instr:<5}{r_res}, {src2}")
            continue

        # ── simple:  result = a ───────────────────────────────
        m = SIMPLE_ASSIGN.match(line)
        if m:
            res, val = m.group(1), m.group(2)
            r_res = alloc.get(res)
            src   = alloc.get(val) if not _is_number(val) else f"#{val}"
            asm.append(f"  MOV  {r_res}, {src}")
            continue

        # comment or folded line – emit as comment
        if '#' in line:
            asm.append(f"  ; {line.strip()}")
            continue

    return asm


def run_codegen(tac_lines: list[str]) -> list[str]:
    asm = generate_code(tac_lines)
    print("\n" + "=" * 55)
    print("  PHASE 6 – TARGET CODE GENERATION  (Assembly)")
    print("=" * 55)
    for line in asm:
        print(line)
    print("=" * 55)
    return asm
