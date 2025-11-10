import argparse
from pathlib import Path
from .lexer import Lexer
from .parser import Parser
from .sema import SemanticAnalyzer
from .codegen_8086 import CodeGen8086


def main():
    ap = argparse.ArgumentParser(description="QuinLang compiler")
    ap.add_argument("source", type=Path, help="Source .ql file")
    ap.add_argument("-o", "--out", type=Path, default=Path("build/out.asm"), help="Output .asm file")
    args = ap.parse_args()

    src_text = args.source.read_text(encoding="utf-8")

    tokens = Lexer(src_text).tokenize()
    ast = Parser(tokens).parse()
    ctx = SemanticAnalyzer().analyze(ast)
    asm = CodeGen8086().generate(ast, ctx)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(asm, encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()