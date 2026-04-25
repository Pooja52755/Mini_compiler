# =============================================================
#  lexer.py  –  Lexical Analysis Phase
#  Converts source code string → list of tokens using regex
# =============================================================

from __future__ import annotations
import re

# ── Token types ──────────────────────────────────────────────
TOKEN_TYPES = [
    ('KEYWORD',   r'\b(int|float|if|else|while|return|print)\b'),
    ('FLOAT',     r'\b\d+\.\d+\b'),
    ('INT',       r'\b\d+\b'),
    ('ID',        r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
    ('RELOP',     r'(==|!=|<=|>=|<|>)'),
    ('ASSIGN',    r'='),
    ('PLUS',      r'\+'),
    ('MINUS',     r'-'),
    ('MUL',       r'\*'),
    ('DIV',       r'/'),
    ('LPAREN',    r'\('),
    ('RPAREN',    r'\)'),
    ('LBRACE',    r'\{'),
    ('RBRACE',    r'\}'),
    ('SEMICOLON', r';'),
    ('COMMA',     r','),
    ('NEWLINE',   r'\n'),
    ('SKIP',      r'[ \t]+'),   # whitespace – discarded
    ('MISMATCH',  r'.'),        # anything else
]

# Pre-compile all patterns into one master regex
MASTER_PATTERN = re.compile(
    '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_TYPES)
)


class Token:
    """Represents a single lexical token."""

    def __init__(self, type_, value, line):
        self.type  = type_
        self.value = value
        self.line  = line

    def __repr__(self):
        return f"Token({self.type:12s}, {self.value!r:15s}, line={self.line})"


def tokenize(source_code: str) -> list[Token]:
    """
    Scans *source_code* and returns a list of Token objects.
    Raises SyntaxError on unrecognised characters.
    """
    tokens   = []
    line_num = 1

    for mo in MASTER_PATTERN.finditer(source_code):
        kind  = mo.lastgroup
        value = mo.group()

        if kind == 'NEWLINE':
            line_num += 1
        elif kind == 'SKIP':
            pass                          # ignore whitespace
        elif kind == 'MISMATCH':
            raise SyntaxError(
                f"[Lexer Error] Unexpected character {value!r} on line {line_num}"
            )
        else:
            tokens.append(Token(kind, value, line_num))

    return tokens


def print_tokens(tokens: list[Token]):
    """Pretty-print token table (for viva / demo)."""
    print("\n" + "=" * 55)
    print("  PHASE 1 – LEXICAL ANALYSIS  (Token Stream)")
    print("=" * 55)
    print(f"  {'TOKEN TYPE':<15} {'VALUE':<20} {'LINE'}")
    print("  " + "-" * 45)
    for tok in tokens:
        print(f"  {tok.type:<15} {tok.value:<20} {tok.line}")
    print("=" * 55)
