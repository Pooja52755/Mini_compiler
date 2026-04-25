#!/usr/bin/env python3
# =============================================================
#  main.py  –  MINI COMPILER  (Menu-Driven Entry Point)
#
#  Option 1: Run full compiler pipeline on sample / user code
#  Option 2: LL(1) grammar demo
#  Option 3: SLR(1) grammar demo
#  Option 4: Exit
# =============================================================

import sys
from lexer    import tokenize, print_tokens
from parser   import run_parser, print_parse_tree
from semantic import run_semantic
from icg      import run_icg
from optimizer import run_optimizer
from codegen  import run_codegen
from ll1      import run_ll1_demo
from slr      import run_slr_demo


# ── Default sample program ────────────────────────────────────
SAMPLE_CODE = """\
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
"""


def print_banner():
    print("""
╔══════════════════════════════════════════════════════╗
║          MINI COMPILER  –  Academic Edition          ║
║         6th Semester  |  Compiler Design Lab         ║
╚══════════════════════════════════════════════════════╝
""")


def print_menu():
    print("""
  ┌──────────────────────────────────────┐
  │  MENU                                │
  │  1. Run Full Compiler Pipeline       │
  │  2. LL(1) Parsing Table Demo         │
  │  3. SLR(1) Parsing Table Demo        │
  │  4. Exit                             │
  └──────────────────────────────────────┘""")


def get_source_code() -> str:
    print("\n  TIP: Declare variables before use, e.g.  int a = 1 + 2;")
    print("  Enter source code line by line.")
    print("  Type a blank line when finished, or press ENTER first for sample.\n")
    lines = []
    while True:
        try:
            line = input("  | ")
        except (EOFError, KeyboardInterrupt):
            break
        if not lines and not line.strip():
            print("\n  [Loading built-in sample code]")
            return SAMPLE_CODE
        if not line.strip() and lines:
            break
        lines.append(line)
    return "\n".join(lines) if lines else SAMPLE_CODE


def run_pipeline(source_code: str):
    print("\n  Source Code:")
    print("  " + "-" * 50)
    for ln in source_code.splitlines():
        print("  " + ln)
    print("  " + "-" * 50)

    try:
        # ── Phase 1: Lexical Analysis ─────────────────────────
        tokens = tokenize(source_code)
        print_tokens(tokens)

        # ── Phase 2: Syntax Analysis ──────────────────────────
        tree = run_parser(tokens)
        print_parse_tree(tree)

        # ── Phase 3: Semantic Analysis ────────────────────────
        sym_table, errors = run_semantic(tree)
        if errors:
            print("\n  [!] Semantic errors present; later phases may be incomplete.")

        # ── Phase 4: Intermediate Code Generation ─────────────
        ctx = run_icg(tree)

        # ── Phase 5 & 6: First generate raw assembly, then optimise ──
        from codegen import generate_code
        raw_asm = generate_code(ctx.tac)

        opt_tac, opt_asm = run_optimizer(ctx.tac, raw_asm)

        # ── Phase 6 (final): Target Code ──────────────────────
        _ = run_codegen(opt_tac)

        print("\n  ✔ Compilation complete!\n")

    except SyntaxError as e:
        print(f"\n  {e}\n")
    except Exception as e:
        print(f"\n  [Unexpected error] {e}\n")
        import traceback; traceback.print_exc()


def main():
    print_banner()

    while True:
        print_menu()
        choice = input("\n  Enter choice (1-4): ").strip()

        if choice == '1':
            source = get_source_code()
            run_pipeline(source)

        elif choice == '2':
            run_ll1_demo()

        elif choice == '3':
            run_slr_demo()

        elif choice == '4':
            print("\n  Goodbye! Happy viva! 🎓\n")
            sys.exit(0)

        else:
            print("  Invalid choice. Please enter 1, 2, 3, or 4.")


if __name__ == '__main__':
    main()
