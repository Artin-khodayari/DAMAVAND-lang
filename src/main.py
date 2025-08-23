import sys
from .lexer import Lexer
from .parser import Parser, ParserError
from .interpreter import Interpreter, RuntimeErrorEx

def main(filename):
    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()

    try:
        tokens = Lexer(code).tokenize()
        ast = Parser(tokens).parse()
        Interpreter().run(ast)
    except (SyntaxError, ParserError, RuntimeErrorEx) as e:
        print(f"[Damavand Error] {e}", file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python src/main.py program.dam")
        sys.exit(1)
    main(sys.argv[1])
