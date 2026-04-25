# =============================================================
#  slr.py  –  SLR(1) Parsing Table Demo
#
#  Steps:
#    1. Augment grammar  S' → S
#    2. Compute LR(0) items / canonical collection
#    3. Compute FOLLOW sets (reused from ll1.py logic)
#    4. Build ACTION and GOTO tables
#    5. Print everything
# =============================================================

from __future__ import annotations
from ll1 import (parse_grammar_input, compute_first,
                  compute_follow, first_of_string,
                  is_terminal, EPSILON, END)

DOT = '•'   # visual separator for LR items


# ── LR(0) Item ───────────────────────────────────────────────
class Item:
    def __init__(self, lhs: str, prod: list[str], dot: int):
        self.lhs  = lhs
        self.prod = prod   # rhs symbols
        self.dot  = dot    # position of •

    def next_symbol(self):
        """Symbol after the dot, or None if dot is at end."""
        if self.dot < len(self.prod):
            s = self.prod[self.dot]
            return None if s == EPSILON else s
        return None

    def advance(self) -> 'Item':
        return Item(self.lhs, self.prod, self.dot + 1)

    def __eq__(self, other):
        return (self.lhs, tuple(self.prod), self.dot) == \
               (other.lhs, tuple(other.prod), other.dot)

    def __hash__(self):
        return hash((self.lhs, tuple(self.prod), self.dot))

    def __repr__(self):
        rhs = list(self.prod)
        rhs.insert(self.dot, DOT)
        return f"[{self.lhs} → {' '.join(rhs)}]"


def closure(items: set[Item], grammar: dict) -> set[Item]:
    changed = True
    while changed:
        changed = False
        for item in list(items):
            sym = item.next_symbol()
            if sym and sym in grammar:
                for prod in grammar[sym]:
                    new = Item(sym, prod, 0)
                    if new not in items:
                        items.add(new)
                        changed = True
    return items


def goto(items: set[Item], symbol: str, grammar: dict) -> set[Item]:
    moved = {item.advance() for item in items if item.next_symbol() == symbol}
    return closure(moved, grammar)


def canonical_collection(grammar: dict, start_prime: str) -> list[set[Item]]:
    """Compute the canonical LR(0) collection."""
    start_item = Item(start_prime, grammar[start_prime][0], 0)
    I0 = closure({start_item}, grammar)
    C  = [I0]
    seen = [frozenset(I0)]
    changed = True
    while changed:
        changed = False
        for I in list(C):
            all_syms = {item.next_symbol() for item in I if item.next_symbol()}
            for sym in all_syms:
                J = goto(I, sym, grammar)
                fJ = frozenset(J)
                if fJ not in seen and J:
                    C.append(J)
                    seen.append(fJ)
                    changed = True
    return C


def build_slr_table(grammar: dict, non_terminals: set,
                    start: str) -> tuple[dict, dict, list, list]:
    """
    Returns (action, goto_t, states, ordered_terminals).
    action[(state, terminal)] = 'sN' | 'rN' | 'acc'
    goto_t[(state, nt)]       = state_number
    """
    # Augment
    start_prime = start + "'"
    aug_grammar  = {start_prime: [[start]], **grammar}
    non_terminals_aug = non_terminals | {start_prime}

    first  = compute_first(aug_grammar, non_terminals_aug)
    follow = compute_follow(aug_grammar, first, non_terminals_aug, start_prime)

    C = canonical_collection(aug_grammar, start_prime)
    state_index = {frozenset(s): i for i, s in enumerate(C)}

    # Collect terminals
    terminals: set[str] = set()
    for prods in aug_grammar.values():
        for prod in prods:
            for sym in prod:
                if is_terminal(sym, non_terminals_aug) and sym != EPSILON:
                    terminals.add(sym)
    terminals.add(END)
    ordered_t = sorted(terminals)

    action: dict = {}
    goto_t: dict = {}
    conflicts = []

    for i, I in enumerate(C):
        for item in I:
            sym = item.next_symbol()
            if sym:
                J  = goto(I, sym, aug_grammar)
                fJ = frozenset(J)
                j  = state_index.get(fJ)
                if j is not None:
                    if is_terminal(sym, non_terminals_aug):
                        key = (i, sym)
                        if key in action and action[key] != f"s{j}":
                            conflicts.append(f"Shift-Reduce conflict at ({i},{sym})")
                        action[key] = f"s{j}"
                    else:
                        goto_t[(i, sym)] = j
            else:
                # dot at end → reduce
                lhs  = item.lhs
                prod = item.prod
                if lhs == start_prime:
                    action[(i, END)] = 'acc'
                else:
                    # Find production number
                    prod_num = _find_prod_num(grammar, lhs, prod)
                    for t in follow[lhs]:
                        key = (i, t)
                        r   = f"r{prod_num}"
                        if key in action and action[key] != r:
                            conflicts.append(
                                f"Reduce-Reduce or S/R conflict at ({i},{t})"
                            )
                        action[key] = r

    return action, goto_t, C, ordered_t, follow, conflicts


def _find_prod_num(grammar: dict, lhs: str, prod: list[str]) -> str:
    """Return 'A→α' label for a production."""
    return f"{lhs}→{''.join(prod)}"


def run_slr_demo():
    print("\n" + "=" * 60)
    print("  SLR(1) PARSING TABLE GENERATOR  (Demo Mode)")
    print("=" * 60)
    print("  Enter grammar rules, one per line.")
    print("  Format:  A -> B C | D | ε")
    print("  Enter a blank line when done.")
    print("-" * 60)

    lines = []
    while True:
        line = input("  > ")
        if not line.strip():
            break
        lines.append(line)

    raw = "\n".join(lines)
    if not raw.strip():
        print("  No grammar entered. Returning to menu.")
        return

    grammar       = parse_grammar_input(raw)
    non_terminals = set(grammar.keys())
    start         = next(iter(grammar))

    action, goto_t, states, ordered_t, follow, conflicts = \
        build_slr_table(grammar, non_terminals, start)

    # ── Print LR(0) items ─────────────────────────────────────
    print(f"\n  LR(0) Canonical Collection  ({len(states)} states):")
    for i, state in enumerate(states):
        print(f"\n    I{i}:")
        for item in sorted(state, key=repr):
            print(f"      {item}")

    # ── FOLLOW sets ───────────────────────────────────────────
    print("\n  FOLLOW Sets:")
    for nt in sorted(non_terminals):
        print(f"    FOLLOW({nt}) = {{ {', '.join(sorted(follow[nt]))} }}")

    # ── ACTION table ──────────────────────────────────────────
    col_w = 14
    print("\n  ACTION Table:")
    header = f"  {'State':<7}" + "".join(f"{t:^{col_w}}" for t in ordered_t)
    print(header)
    print("  " + "-" * (7 + col_w * len(ordered_t)))
    for i in range(len(states)):
        row = f"  {i:<7}"
        for t in ordered_t:
            cell = action.get((i, t), "")
            row += f"{cell:^{col_w}}"
        print(row)

    # ── GOTO table ────────────────────────────────────────────
    nts_sorted = sorted(non_terminals)
    print("\n  GOTO Table:")
    header = f"  {'State':<7}" + "".join(f"{nt:^{col_w}}" for nt in nts_sorted)
    print(header)
    print("  " + "-" * (7 + col_w * len(nts_sorted)))
    for i in range(len(states)):
        row = f"  {i:<7}"
        for nt in nts_sorted:
            cell = str(goto_t.get((i, nt), ""))
            row += f"{cell:^{col_w}}"
        print(row)

    if conflicts:
        print("\n  ⚠ Conflicts detected (grammar may not be SLR(1)):")
        for c in conflicts:
            print(f"    • {c}")
    else:
        print("\n  ✔ No conflicts. Grammar is SLR(1).")
    print("=" * 60)
