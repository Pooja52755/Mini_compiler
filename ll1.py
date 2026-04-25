# =============================================================
#  ll1.py  –  LL(1) Parsing Table Generator  (Demo Mode)
#
#  Given a grammar in text form the module:
#    1. Computes FIRST sets for every non-terminal
#    2. Computes FOLLOW sets
#    3. Builds the LL(1) parse table
#    4. Prints everything neatly
# =============================================================

# ── Grammar representation ────────────────────────────────────
# We store grammar as { NonTerminal: [ [symbol, ...], ... ] }
# Epsilon is represented by the string 'ε'

from __future__ import annotations

EPSILON = 'ε'
END     = '$'


def parse_grammar_input(raw: str) -> dict[str, list[list[str]]]:
    """
    Parse grammar rules entered by the user.
    Format per line:  A -> B C | D | ε
    Returns dict: { 'A': [['B','C'], ['D'], ['ε']], ... }
    """
    grammar: dict[str, list[list[str]]] = {}
    for line in raw.strip().splitlines():
        line = line.strip()
        if not line or '->' not in line:
            continue
        lhs, rhs = line.split('->', 1)
        lhs  = lhs.strip()
        prods = [p.strip().split() for p in rhs.split('|')]
        grammar[lhs] = prods
    return grammar


def is_terminal(symbol: str, non_terminals: set[str]) -> bool:
    return symbol not in non_terminals and symbol != EPSILON


def compute_first(grammar: dict, non_terminals: set) -> dict[str, set[str]]:
    """FIRST(X) = set of terminals that can begin any string derived from X."""
    first: dict[str, set[str]] = {nt: set() for nt in non_terminals}

    changed = True
    while changed:
        changed = False
        for nt, prods in grammar.items():
            for prod in prods:
                if prod == [EPSILON]:
                    if EPSILON not in first[nt]:
                        first[nt].add(EPSILON)
                        changed = True
                    continue
                for sym in prod:
                    if is_terminal(sym, non_terminals):
                        if sym not in first[nt]:
                            first[nt].add(sym)
                            changed = True
                        break
                    else:
                        before = len(first[nt])
                        first[nt] |= (first[sym] - {EPSILON})
                        if len(first[nt]) > before:
                            changed = True
                        if EPSILON not in first[sym]:
                            break
                else:
                    if EPSILON not in first[nt]:
                        first[nt].add(EPSILON)
                        changed = True
    return first


def first_of_string(symbols: list[str], first: dict, non_terminals: set) -> set[str]:
    result = set()
    for sym in symbols:
        if sym == EPSILON:
            result.add(EPSILON)
            break
        if is_terminal(sym, non_terminals):
            result.add(sym)
            break
        result |= (first[sym] - {EPSILON})
        if EPSILON not in first[sym]:
            break
    else:
        result.add(EPSILON)
    return result


def compute_follow(grammar: dict, first: dict, non_terminals: set, start: str) \
        -> dict[str, set[str]]:
    follow: dict[str, set[str]] = {nt: set() for nt in non_terminals}
    follow[start].add(END)

    changed = True
    while changed:
        changed = False
        for nt, prods in grammar.items():
            for prod in prods:
                for i, sym in enumerate(prod):
                    if sym in non_terminals:
                        beta        = prod[i+1:] or [EPSILON]
                        first_beta  = first_of_string(beta, first, non_terminals)
                        before      = len(follow[sym])
                        follow[sym] |= (first_beta - {EPSILON})
                        if EPSILON in first_beta:
                            follow[sym] |= follow[nt]
                        if len(follow[sym]) > before:
                            changed = True
    return follow


def build_ll1_table(grammar: dict, first: dict, follow: dict,
                    non_terminals: set) -> dict:
    """
    Returns table: { (NonTerminal, terminal): production_list }
    """
    table: dict = {}
    for nt, prods in grammar.items():
        for prod in prods:
            first_prod = first_of_string(prod, first, non_terminals)
            for terminal in first_prod:
                if terminal != EPSILON:
                    key = (nt, terminal)
                    if key in table:
                        table[key] = table[key] + [" | "] + prod  # conflict
                    else:
                        table[key] = prod
            if EPSILON in first_prod:
                for terminal in follow[nt]:
                    key = (nt, terminal)
                    if key in table:
                        table[key] = table[key] + [" | "] + prod
                    else:
                        table[key] = prod
    return table


def run_ll1_demo():
    print("\n" + "=" * 60)
    print("  LL(1) PARSING TABLE GENERATOR  (Demo Mode)")
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

    grammar      = parse_grammar_input(raw)
    non_terminals = set(grammar.keys())
    start         = next(iter(grammar))      # first NT is start

    first  = compute_first(grammar, non_terminals)
    follow = compute_follow(grammar, first, non_terminals, start)
    table  = build_ll1_table(grammar, first, follow, non_terminals)

    # ── Collect all terminals ─────────────────────────────────
    terminals = set()
    for prods in grammar.values():
        for prod in prods:
            for sym in prod:
                if is_terminal(sym, non_terminals) and sym != EPSILON:
                    terminals.add(sym)
    terminals.add(END)
    terminals = sorted(terminals)

    # ── FIRST sets ────────────────────────────────────────────
    print("\n  FIRST Sets:")
    for nt in sorted(non_terminals):
        print(f"    FIRST({nt}) = {{ {', '.join(sorted(first[nt]))} }}")

    # ── FOLLOW sets ───────────────────────────────────────────
    print("\n  FOLLOW Sets:")
    for nt in sorted(non_terminals):
        print(f"    FOLLOW({nt}) = {{ {', '.join(sorted(follow[nt]))} }}")

    # ── Parse table ───────────────────────────────────────────
    print("\n  LL(1) Parse Table:")
    col_w = 18
    header = f"  {'NT':<10}" + "".join(f"{t:^{col_w}}" for t in terminals)
    print(header)
    print("  " + "-" * (10 + col_w * len(terminals)))
    for nt in sorted(non_terminals):
        row = f"  {nt:<10}"
        for t in terminals:
            prod = table.get((nt, t))
            cell = " ".join(prod) if prod else ""
            if len(cell) > col_w - 2:
                cell = cell[:col_w-5] + "..."
            row += f"{cell:^{col_w}}"
        print(row)

    print("\n  (Conflicts shown as  'prod1 | prod2'  in a cell)")
    print("=" * 60)
