# MINI COMPILER – Academic Project Documentation
## 6th Semester | Compiler Design Lab

---

## PROJECT STRUCTURE

```
mini_compiler/
│
├── main.py        ← Menu-driven entry point
├── lexer.py       ← Phase 1: Lexical Analysis
├── parser.py      ← Phase 2: Syntax Analysis (Recursive Descent)
├── semantic.py    ← Phase 3: Semantic Analysis + Symbol Table
├── icg.py         ← Phase 4: Intermediate Code Generation
├── optimizer.py   ← Phase 5: Code Optimization
├── codegen.py     ← Phase 6: Target Code Generation
├── ll1.py         ← Demo: LL(1) Parsing Table
└── slr.py         ← Demo: SLR(1) Parsing Table
```

---

## HOW TO RUN

```bash
cd mini_compiler
python3 main.py
```

---

## MODULE EXPLANATIONS

### 1. lexer.py — Lexical Analysis
- Uses Python `re` module with a single master regex (regex-based tokenizer).
- Matches all token types in priority order: KEYWORD before ID, FLOAT before INT.
- Returns a list of `Token(type, value, line)` objects.
- Raises `SyntaxError` on unrecognised characters.

### 2. parser.py — Syntax Analysis
- Implements a hand-written **Recursive Descent Parser**.
- Each grammar rule has a corresponding `parse_X()` method.
- Builds a `ParseNode` tree for the whole program.
- `print_tree()` renders it with box-drawing characters.

### 3. semantic.py — Semantic Analysis
- Walks the parse tree top-down.
- Maintains a flat `SymbolTable` (dict of `Symbol` objects).
- Reports: undeclared variables, redeclarations.
- In real compilers: also checks type compatibility, scope rules.

### 4. icg.py — Intermediate Code Generation
- Uses the tree-walk approach.
- Generates **temporary variables** (t1, t2, …) and **labels** (L1, L2, …).
- Emits TAC, Triples, and Quadruples simultaneously.
- if-else and while generate correct jump code.

### 5. optimizer.py — Code Optimization
- **Constant Folding**: evaluates constant expressions at compile time
  using regex to detect `result = NUM op NUM` patterns.
- **Peephole**: scans assembly lines; removes `MOV Rx, Rx` and
  consecutive duplicate instructions.

### 6. codegen.py — Target Code Generation
- Simple register allocator: round-robin over R0–R4.
- Translates TAC instructions into MOV / ADD / SUB / MUL / DIV /
  CMP / JZ / JMP / PRINT instructions.

### 7. ll1.py — LL(1) Table Generator
- Computes FIRST and FOLLOW sets using iterative fixed-point algorithm.
- Builds the LL(1) parse table cell by cell.
- Detects and reports conflicts.

### 8. slr.py — SLR(1) Table Generator
- Augments grammar with S' → S.
- Computes canonical LR(0) collection via closure/goto.
- Uses FOLLOW sets (from ll1.py) to fill REDUCE entries.
- Fills ACTION (shift/reduce/accept) and GOTO tables.

---

## SAMPLE INPUT / OUTPUT

### Input (default sample code):
```
int a = 3 + 4;
int b = 2;
int c = a + b;
int result = 0;
if (c > 5) {
    result = c + 1;
} else {
    result = b;
}
print(result);
```

### Phase 1 Output (Tokens):
```
KEYWORD         int                  1
ID              a                    1
ASSIGN          =                    1
INT             3                    1
PLUS            +                    1
INT             4                    1
...
```

### Phase 4 Output (TAC):
```
  t1 = 3 + 4
  a = t1
  b = 2
  t2 = a + b
  c = t2
  result = 0
  t3 = c > 5
  if_false t3 goto L1
  t4 = c + 1
  result = t4
  goto L2
L1:
  result = b
L2:
  print result
```

### Phase 5 Output (after Constant Folding):
```
  t1 = 7      # folded: 3+4
  t2 = 9      # folded: 7+2
  t3 = 1      # folded: 9>5
  t4 = 10     # folded: 9+1
```

---

## LL(1) Demo — Sample Grammar Input

```
E -> T E'
E' -> + T E' | ε
T -> F T'
T' -> * F T' | ε
F -> ( E ) | id
```

---

## SLR(1) Demo — Sample Grammar Input

```
S -> E
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
```

---
*End of Documentation*
