import sys
from src.damavand import Damavand   # assuming your class is in damavand.py

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py program.dam")
        return

    filename = sys.argv[1]
    if not filename.endswith(".dam"):
        print("Error: expected a .dam file")
        return

    try:
        with open(filename, "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Error: file '{filename}' not found")
        return

    Damavand().run(code)

if __name__ == "__main__":
    main()
