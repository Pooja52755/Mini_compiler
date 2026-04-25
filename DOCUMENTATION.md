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

## VIVA QUESTIONS & ANSWERS

---

### PHASE 1 – LEXICAL ANALYSIS

**Q1. What is lexical analysis?**
A: Lexical analysis is the first phase of a compiler. It reads the source code
character by character and groups them into meaningful units called **tokens**.
Each token has a type (e.g. KEYWORD, ID, INT) and a value (e.g. "if", "a", "5").

**Q2. What is a token? Give examples.**
A: A token is a pair (token_type, attribute_value).
Examples: (KEYWORD, "int"), (ID, "x"), (INT, "42"), (PLUS, "+").

**Q3. What is a lexeme?**
A: A lexeme is the actual string in the source code matched to a token pattern.
For the token (KEYWORD, "while"), the lexeme is "while".

**Q4. What is the difference between DFA and regex-based lexers?**
A: Both are equivalent in power (both recognise regular languages). A DFA-based
lexer is typically faster but harder to write. A regex-based lexer (like ours)
is easier to write and maintain; under the hood, Python compiles regex to DFA.

**Q5. What does your lexer do with whitespace?**
A: Whitespace matches the SKIP pattern and is silently discarded. Newlines
increment the line counter for accurate error reporting.

---

### PHASE 2 – SYNTAX ANALYSIS

**Q6. What is syntax analysis / parsing?**
A: Parsing is the second phase that checks whether the token stream follows
the grammar rules of the language and constructs a **parse tree**.

**Q7. What is a recursive descent parser?**
A: A recursive descent parser is a top-down parser where each non-terminal in
the grammar has a corresponding function. Each function consumes tokens and
calls other functions recursively. It is easy to write by hand.

**Q8. What is a parse tree?**
A: A parse tree is a tree that shows how the source code is derived from the
grammar. The root is the start symbol, leaves are terminals (tokens), and
internal nodes are non-terminals.

**Q9. What is the difference between a parse tree and an AST?**
A: A parse tree includes all grammar symbols including redundant ones (like
parentheses). An Abstract Syntax Tree (AST) removes redundant nodes and keeps
only the essential structure.

**Q10. What grammar does your parser implement?**
A:
```
program    → stmt*
stmt       → decl_stmt | assign_stmt | if_stmt | while_stmt | print_stmt
decl_stmt  → TYPE ID (= expr)? ;
assign_stmt→ ID = expr ;
if_stmt    → if ( expr ) { stmt* } (else { stmt* })?
while_stmt → while ( expr ) { stmt* }
print_stmt → print ( expr ) ;
expr       → term ((+|-|relop) term)*
term       → factor ((*|/) factor)*
factor     → INT | FLOAT | ID | ( expr )
```

---

### PHASE 3 – SEMANTIC ANALYSIS

**Q11. What is semantic analysis?**
A: Semantic analysis checks the meaning of the program beyond syntax.
It ensures variables are declared before use, types are compatible,
function calls match signatures, etc.

**Q12. What is a symbol table?**
A: A symbol table is a data structure (usually a hash map) that stores
information about identifiers: name, type, scope, memory location.
It is created during semantic analysis and used by all later phases.

**Q13. What errors does your semantic analyser detect?**
A: (1) Undeclared variable usage, (2) Variable redeclaration.
In an extended compiler we would also check type mismatches.

**Q14. What is scope?**
A: Scope is the region of the program where an identifier is visible.
Our mini compiler uses a single global scope. Real compilers use stacked
(nested) symbol tables for block-scoped languages.

---

### PHASE 4 – INTERMEDIATE CODE GENERATION

**Q15. What is intermediate code? Why is it used?**
A: Intermediate code (IR) is a machine-independent representation between
the source and target. Benefits:
(1) Portability – same front-end can target multiple machines.
(2) Optimisation – easier to optimise IR than source or machine code.
(3) Separation of concerns between front-end and back-end.

**Q16. What is Three Address Code (TAC)?**
A: TAC is an IR where each instruction has at most one operator and
at most three operands (result, arg1, arg2). Example: `t1 = a + b`.

**Q17. Explain Triples and Quadruples.**
A: Both are tabular representations of TAC instructions.
- **Triples**: (op, arg1, arg2) — result is implied by position (index).
- **Quadruples**: (op, arg1, arg2, result) — result is explicit.
Quadruples are preferred because they don't need to be reordered when
the code is rearranged (unlike triples).

**Q18. How do you handle if-else in TAC?**
A: We compute the condition into a temp, then emit:
```
  if_false cond goto L_else
  [if-body code]
  goto L_end
L_else:
  [else-body code]
L_end:
```

---

### PHASE 5 – CODE OPTIMIZATION

**Q19. What is constant folding?**
A: Constant folding evaluates constant expressions at compile time so they
don't need to be evaluated at runtime. Example: `t1 = 3 + 4` → `t1 = 7`.

**Q20. What is peephole optimisation?**
A: Peephole optimisation examines a small sliding window ("peephole") of
instructions and replaces inefficient patterns with better ones.
Common examples: removing `MOV R0, R0`, replacing `t = x; x = t` with nothing.

**Q21. What is the difference between machine-independent and machine-dependent optimisation?**
A:
- **Machine-independent**: works on IR, applies to any target.
  Examples: constant folding, dead code elimination, common subexpression elimination.
- **Machine-dependent**: targets specific hardware features.
  Examples: using special instructions, register allocation, peephole on assembly.

**Q22. Name any four other optimisation techniques.**
A: (1) Dead code elimination, (2) Common subexpression elimination,
(3) Loop invariant code motion, (4) Strength reduction (x*2 → x<<1).

---

### PHASE 6 – TARGET CODE GENERATION

**Q23. What is target code generation?**
A: The final phase translates optimised IR into machine/assembly code for
the target architecture. It involves instruction selection, register allocation,
and instruction scheduling.

**Q24. What is register allocation?**
A: Register allocation decides which variables/temporaries are kept in registers
(fast) vs. spilled to memory (slow). Our mini compiler uses a simple round-robin
allocator over R0–R4.

---

### PARSING THEORY

**Q25. What is LL(1) parsing?**
A: LL(1) stands for:
- **L**: scan input Left to right
- **L**: construct Leftmost derivation
- **(1)**: look-ahead of 1 token
It uses a parse table indexed by (non-terminal, lookahead) to decide which
production to apply.

**Q26. What are FIRST and FOLLOW sets?**
A:
- **FIRST(A)**: set of terminals that can appear at the start of any string
  derived from A. Used to fill LL(1) table entries.
- **FOLLOW(A)**: set of terminals that can appear immediately after A in
  any sentential form. Used to handle ε-productions.

**Q27. What is SLR(1) parsing?**
A: SLR (Simple LR) is a bottom-up parser:
- **L**: scan Left to right
- **R**: construct Rightmost derivation in reverse
- **(1)**: 1 token look-ahead
It uses the canonical LR(0) item sets + FOLLOW sets to build ACTION/GOTO tables.

**Q28. What is an LR(0) item?**
A: An LR(0) item is a production with a dot (•) marking how much has been
seen. Example: `E → E • + T` means we have seen `E` and are expecting `+ T`.

**Q29. What is the difference between SLR, CLR, and LALR parsers?**
A:
| Parser | Power  | Table size | Complexity |
|--------|--------|------------|------------|
| SLR(1) | Least  | Smaller    | Lowest     |
| LALR(1)| Medium | Same as SLR| Medium     |
| CLR(1) | Most   | Largest    | Highest    |
Most production compilers (yacc/bison) use LALR(1).

**Q30. What is a shift-reduce conflict?**
A: A conflict in the parse table where the parser cannot decide whether to
**shift** the next input token or **reduce** by a production. It means the
grammar is ambiguous or not suitable for the chosen parsing method.

---

*End of Documentation*
