# =============================================================
#  icg.py  –  Intermediate Code Generation Phase
#  Produces:
#    1. Three Address Code (TAC)
#    2. Triples
#    3. Quadruples
#  Works by walking the parse tree and emitting temp variables.
# =============================================================

from __future__ import annotations
from parser import ParseNode


class ICGContext:
    """Holds state for the ICG pass."""

    def __init__(self):
        self._temp_count  = 0
        self._label_count = 0
        self.tac: list[str]             = []   # Three Address Code strings
        self.triples: list[tuple]       = []   # (op, arg1, arg2)
        self.quadruples: list[tuple]    = []   # (op, arg1, arg2, result)

    # ── Temp and label generators ─────────────────────────────
    def new_temp(self) -> str:
        self._temp_count += 1
        return f"t{self._temp_count}"

    def new_label(self) -> str:
        self._label_count += 1
        return f"L{self._label_count}"

    # ── Emit helpers ──────────────────────────────────────────
    def emit(self, result, op, arg1, arg2=""):
        """Record one instruction in all three IR forms."""
        # TAC  e.g.  "t1 = a + b"  or  "t1 = a"
        if op == '=':
            self.tac.append(f"  {result} = {arg1}")
            self.triples.append(('=', arg1, ''))
            self.quadruples.append(('=', arg1, '', result))
        else:
            rhs = f"{arg1} {op} {arg2}" if arg2 != "" else f"{arg1}"
            self.tac.append(f"  {result} = {rhs}")
            self.triples.append((op, arg1, arg2))
            self.quadruples.append((op, arg1, arg2, result))

    def emit_label(self, label: str):
        self.tac.append(f"{label}:")
        self.triples.append(('label', label, ''))
        self.quadruples.append(('label', label, '', ''))

    def emit_goto(self, label: str):
        self.tac.append(f"  goto {label}")
        self.triples.append(('goto', label, ''))
        self.quadruples.append(('goto', label, '', ''))

    def emit_if_false(self, cond: str, label: str):
        self.tac.append(f"  if_false {cond} goto {label}")
        self.triples.append(('if_false', cond, label))
        self.quadruples.append(('if_false', cond, label, ''))

    def emit_print(self, val: str):
        self.tac.append(f"  print {val}")
        self.triples.append(('print', val, ''))
        self.quadruples.append(('print', val, '', ''))


# ── Tree walker ───────────────────────────────────────────────
def gen_expr(node: ParseNode, ctx: ICGContext) -> str:
    """Return the temp/variable/constant that holds the expr result."""
    if node.label == "factor":
        val = node.value
        # Grouped expression:  factor → ( expr )  has children, no value
        if val is None:
            return gen_expr(node.children[0], ctx)
        if val.startswith("INT(") or val.startswith("FLOAT("):
            return val[val.index("(")+1:-1]   # just the numeric string
        elif val.startswith("ID("):
            return val[3:-1]
        else:
            # fallback – treat as grouped child
            return gen_expr(node.children[0], ctx)

    # expr or term: children are [operand, op, operand, op, operand ...]
    if node.label in ("expr", "term"):
        children = node.children
        result   = gen_expr(children[0], ctx)
        i = 1
        while i < len(children):
            op    = children[i].value
            right = gen_expr(children[i+1], ctx)
            t     = ctx.new_temp()
            ctx.emit(t, op, result, right)
            result = t
            i += 2
        return result

    return "?"


def gen_stmt(node: ParseNode, ctx: ICGContext):
    if node.label == "program":
        for child in node.children:
            gen_stmt(child, ctx)

    elif node.label == "decl_stmt":
        name = node.children[1].value
        if len(node.children) > 2:           # has initializer
            val = gen_expr(node.children[2], ctx)
            ctx.emit(name, '=', val)

    elif node.label == "assign_stmt":
        name = node.children[0].value
        val  = gen_expr(node.children[1], ctx)
        ctx.emit(name, '=', val)

    elif node.label == "if_stmt":
        cond      = gen_expr(node.children[0], ctx)
        else_lbl  = ctx.new_label()
        end_lbl   = ctx.new_label()
        ctx.emit_if_false(cond, else_lbl)
        gen_stmt(node.children[1], ctx)          # if_body
        ctx.emit_goto(end_lbl)
        ctx.emit_label(else_lbl)
        if len(node.children) > 2:               # else_body
            gen_stmt(node.children[2], ctx)
        ctx.emit_label(end_lbl)

    elif node.label == "while_stmt":
        start_lbl = ctx.new_label()
        end_lbl   = ctx.new_label()
        ctx.emit_label(start_lbl)
        cond = gen_expr(node.children[0], ctx)
        ctx.emit_if_false(cond, end_lbl)
        gen_stmt(node.children[1], ctx)           # while_body
        ctx.emit_goto(start_lbl)
        ctx.emit_label(end_lbl)

    elif node.label in ("if_body", "else_body", "while_body"):
        for child in node.children:
            gen_stmt(child, ctx)

    elif node.label == "print_stmt":
        val = gen_expr(node.children[0], ctx)
        ctx.emit_print(val)


def run_icg(tree: ParseNode) -> ICGContext:
    ctx = ICGContext()
    gen_stmt(tree, ctx)
    _print_icg(ctx)
    return ctx


def _print_icg(ctx: ICGContext):
    print("\n" + "=" * 55)
    print("  PHASE 4 – INTERMEDIATE CODE GENERATION")
    print("=" * 55)

    # ── TAC ──────────────────────────────────────────────────
    print("\n  ── (a) Three Address Code (TAC) ──")
    for line in ctx.tac:
        print(line)

    # ── Triples ───────────────────────────────────────────────
    print("\n  ── (b) Triples ──")
    print(f"  {'#':<5} {'OP':<12} {'ARG1':<12} {'ARG2'}")
    print("  " + "-" * 42)
    for i, (op, a1, a2) in enumerate(ctx.triples):
        print(f"  {i:<5} {op:<12} {str(a1):<12} {a2}")

    # ── Quadruples ────────────────────────────────────────────
    print("\n  ── (c) Quadruples ──")
    print(f"  {'#':<5} {'OP':<12} {'ARG1':<12} {'ARG2':<12} {'RESULT'}")
    print("  " + "-" * 53)
    for i, (op, a1, a2, res) in enumerate(ctx.quadruples):
        print(f"  {i:<5} {op:<12} {str(a1):<12} {str(a2):<12} {res}")
    print("=" * 55)
