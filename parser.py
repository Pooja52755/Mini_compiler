# =============================================================
#  parser.py  –  Syntax Analysis Phase
#  Recursive-Descent Parser → builds a ParseTree
#
#  Grammar (simplified):
#   program    → stmt*
#   stmt       → decl_stmt | assign_stmt | if_stmt
#                | while_stmt | print_stmt
#   decl_stmt  → TYPE ID (= expr)? ;
#   assign_stmt→ ID = expr ;
#   if_stmt    → if ( expr ) { stmt* } (else { stmt* })?
#   while_stmt → while ( expr ) { stmt* }
#   print_stmt → print ( expr ) ;
#   expr       → term ((+|-) term)*
#   term       → factor ((*|/) factor)*
#   factor     → INT | FLOAT | ID | ( expr )
# =============================================================

from __future__ import annotations
from lexer import Token


# ── Parse-tree node ──────────────────────────────────────────
class ParseNode:
    def __init__(self, label, children=None, value=None):
        self.label    = label          # e.g. 'expr', 'stmt'
        self.value    = value          # leaf value if terminal
        self.children = children or []

    def add_child(self, node):
        self.children.append(node)

    def __repr__(self):
        return f"<{self.label}>" if not self.value else f"[{self.label}={self.value}]"


def print_tree(node: ParseNode, prefix="", is_last=True):
    """Recursively print the parse tree in a visual tree style."""
    connector = "└── " if is_last else "├── "
    line = prefix + connector + str(node)
    print(line)
    child_prefix = prefix + ("    " if is_last else "│   ")
    for i, child in enumerate(node.children):
        print_tree(child, child_prefix, i == len(node.children) - 1)


# ── Recursive-descent parser ─────────────────────────────────
class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens  = tokens
        self.pos     = 0

    # ── Helpers ──────────────────────────────────────────────
    def current(self) -> Token | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def peek_type(self) -> str | None:
        tok = self.current()
        return tok.type if tok else None

    def consume(self, expected_type=None, expected_value=None) -> Token:
        tok = self.current()
        if tok is None:
            raise SyntaxError("[Parser Error] Unexpected end of input.")
        if expected_type and tok.type != expected_type:
            raise SyntaxError(
                f"[Parser Error] Line {tok.line}: expected {expected_type!r}, "
                f"got {tok.type!r} ({tok.value!r})"
            )
        if expected_value and tok.value != expected_value:
            raise SyntaxError(
                f"[Parser Error] Line {tok.line}: expected {expected_value!r}, "
                f"got {tok.value!r}"
            )
        self.pos += 1
        return tok

    # ── Grammar rules ─────────────────────────────────────────
    def parse_program(self) -> ParseNode:
        root = ParseNode("program")
        while self.current() is not None:
            root.add_child(self.parse_stmt())
        return root

    def parse_stmt(self) -> ParseNode:
        tok = self.current()
        if tok is None:
            raise SyntaxError("[Parser Error] Expected statement, got EOF.")

        if tok.type == 'KEYWORD' and tok.value in ('int', 'float'):
            return self.parse_decl_stmt()
        elif tok.type == 'KEYWORD' and tok.value == 'if':
            return self.parse_if_stmt()
        elif tok.type == 'KEYWORD' and tok.value == 'while':
            return self.parse_while_stmt()
        elif tok.type == 'KEYWORD' and tok.value == 'print':
            return self.parse_print_stmt()
        elif tok.type == 'ID':
            return self.parse_assign_stmt()
        else:
            raise SyntaxError(
                f"[Parser Error] Line {tok.line}: unknown statement starting with {tok.value!r}"
            )

    def parse_decl_stmt(self) -> ParseNode:
        node = ParseNode("decl_stmt")
        dtype = self.consume('KEYWORD')
        node.add_child(ParseNode("type", value=dtype.value))
        idn = self.consume('ID')
        node.add_child(ParseNode("ID", value=idn.value))
        if self.peek_type() == 'ASSIGN':
            self.consume('ASSIGN')
            node.add_child(self.parse_expr())
        self.consume('SEMICOLON')
        return node

    def parse_assign_stmt(self) -> ParseNode:
        node = ParseNode("assign_stmt")
        idn = self.consume('ID')
        node.add_child(ParseNode("ID", value=idn.value))
        self.consume('ASSIGN')
        node.add_child(self.parse_expr())
        self.consume('SEMICOLON')
        return node

    def parse_if_stmt(self) -> ParseNode:
        node = ParseNode("if_stmt")
        self.consume('KEYWORD', 'if')
        self.consume('LPAREN')
        node.add_child(self.parse_expr())
        self.consume('RPAREN')
        self.consume('LBRACE')
        body = ParseNode("if_body")
        while self.peek_type() != 'RBRACE':
            body.add_child(self.parse_stmt())
        self.consume('RBRACE')
        node.add_child(body)
        if self.peek_type() == 'KEYWORD' and self.current().value == 'else':
            self.consume('KEYWORD', 'else')
            self.consume('LBRACE')
            else_body = ParseNode("else_body")
            while self.peek_type() != 'RBRACE':
                else_body.add_child(self.parse_stmt())
            self.consume('RBRACE')
            node.add_child(else_body)
        return node

    def parse_while_stmt(self) -> ParseNode:
        node = ParseNode("while_stmt")
        self.consume('KEYWORD', 'while')
        self.consume('LPAREN')
        node.add_child(self.parse_expr())
        self.consume('RPAREN')
        self.consume('LBRACE')
        body = ParseNode("while_body")
        while self.peek_type() != 'RBRACE':
            body.add_child(self.parse_stmt())
        self.consume('RBRACE')
        node.add_child(body)
        return node

    def parse_print_stmt(self) -> ParseNode:
        node = ParseNode("print_stmt")
        self.consume('KEYWORD', 'print')
        self.consume('LPAREN')
        node.add_child(self.parse_expr())
        self.consume('RPAREN')
        self.consume('SEMICOLON')
        return node

    # ── Expressions (left-recursive handled iteratively) ──────
    def parse_expr(self) -> ParseNode:
        node = ParseNode("expr")
        node.add_child(self.parse_term())
        while self.peek_type() in ('PLUS', 'MINUS', 'RELOP'):
            op = self.consume()
            node.add_child(ParseNode("op", value=op.value))
            node.add_child(self.parse_term())
        return node

    def parse_term(self) -> ParseNode:
        node = ParseNode("term")
        node.add_child(self.parse_factor())
        while self.peek_type() in ('MUL', 'DIV'):
            op = self.consume()
            node.add_child(ParseNode("op", value=op.value))
            node.add_child(self.parse_factor())
        return node

    def parse_factor(self) -> ParseNode:
        tok = self.current()
        if tok is None:
            raise SyntaxError("[Parser Error] Expected factor, got EOF.")
        if tok.type == 'INT':
            self.consume()
            return ParseNode("factor", value=f"INT({tok.value})")
        elif tok.type == 'FLOAT':
            self.consume()
            return ParseNode("factor", value=f"FLOAT({tok.value})")
        elif tok.type == 'ID':
            self.consume()
            return ParseNode("factor", value=f"ID({tok.value})")
        elif tok.type == 'LPAREN':
            self.consume('LPAREN')
            node = ParseNode("factor")
            node.add_child(self.parse_expr())
            self.consume('RPAREN')
            return node
        else:
            raise SyntaxError(
                f"[Parser Error] Line {tok.line}: unexpected token {tok.value!r} in expression"
            )


def run_parser(tokens: list[Token]) -> ParseNode:
    p = Parser(tokens)
    tree = p.parse_program()
    return tree


def print_parse_tree(tree: ParseNode):
    print("\n" + "=" * 55)
    print("  PHASE 2 – SYNTAX ANALYSIS  (Parse Tree)")
    print("=" * 55)
    print_tree(tree, "", True)
    print("=" * 55)
