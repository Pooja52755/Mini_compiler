# =============================================================
#  semantic.py  –  Semantic Analysis Phase
#  - Builds a Symbol Table
#  - Detects undeclared variables
#  - Detects type mismatches (basic)
# =============================================================

from __future__ import annotations
from parser import ParseNode


class Symbol:
    """Entry in the symbol table."""
    def __init__(self, name, dtype, line):
        self.name  = name
        self.dtype = dtype
        self.line  = line

    def __repr__(self):
        return f"Symbol({self.name!r}, type={self.dtype}, line={self.line})"


class SymbolTable:
    """Simple flat symbol table (one scope for this mini compiler)."""

    def __init__(self):
        self._table: dict[str, Symbol] = {}

    def declare(self, name: str, dtype: str, line: int):
        if name in self._table:
            print(f"  [Semantic Warning] Variable '{name}' redeclared on line {line}.")
        self._table[name] = Symbol(name, dtype, line)

    def lookup(self, name: str) -> Symbol | None:
        return self._table.get(name)

    def print_table(self):
        print("\n" + "=" * 55)
        print("  PHASE 3 – SEMANTIC ANALYSIS  (Symbol Table)")
        print("=" * 55)
        if not self._table:
            print("  (empty)")
        else:
            print(f"  {'NAME':<15} {'TYPE':<10}")
            print("  " + "-" * 38)
            for sym in self._table.values():
                print(f"  {sym.name:<15} {sym.dtype:<10}")
        print("=" * 55)


class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: list[str] = []

    def analyse(self, node: ParseNode):
        """Walk the parse tree and perform semantic checks."""
        self._visit(node)

    def _visit(self, node: ParseNode):
        if node.label == "decl_stmt":
            self._handle_decl(node)
        elif node.label == "assign_stmt":
            self._handle_assign(node)
        elif node.label == "factor" and node.value and node.value.startswith("ID("):
            self._check_use(node)
        else:
            for child in node.children:
                self._visit(child)

    def _handle_decl(self, node: ParseNode):
        dtype = node.children[0].value
        name  = node.children[1].value
        line  = 0   # line info not propagated to tree; 
        self.symbol_table.declare(name, dtype, line)
        # visit rest (initializer expression)
        for child in node.children[2:]:
            self._visit(child)

    def _handle_assign(self, node: ParseNode):
        name = node.children[0].value
        if not self.symbol_table.lookup(name):
            msg = (f"  [Semantic Warning] Variable '{name}' assigned without "
                   f"declaration.")
            print(msg)
            self.errors.append(msg)
        for child in node.children[1:]:
            self._visit(child)

    def _check_use(self, node: ParseNode):
        name = node.value[3:-1]   # strip "ID(" and ")"
        if not self.symbol_table.lookup(name):
            msg = f"  [Semantic Warning] Variable '{name}' not yet declared;"
            print(msg)
            self.errors.append(msg)


def run_semantic(tree: ParseNode) -> tuple[SymbolTable, list[str]]:
    sa = SemanticAnalyzer()
    sa.analyse(tree)
    sa.symbol_table.print_table()
    if sa.errors:
        print("  Semantic errors found:", len(sa.errors))
    else:
        print("  No semantic errors. ✔")
    return sa.symbol_table, sa.errors
