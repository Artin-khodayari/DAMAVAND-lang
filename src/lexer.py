import re

class Token:
    def __init__(self, type_, value, line, col):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {self.value}, {self.line}:{self.col})"


class Lexer:
    KEYWORDS = {
        "fff": "FFF",
        "if": "IF",
        "else": "ELSE",
        "while": "WHILE",
        "print": "PRINT",
        "true": "TRUE",
        "false": "FALSE",
    }

    TOKEN_SPEC = [
        ("COMMENT",  r"#.*"),
        ("NUMBER",   r"\d+(\.\d+)?"),
        ("STRING",   r"\"([^\"\\]|\\.)*\"|'([^'\\]|\\.)*'"),
        ("ID",       r"[A-Za-z_][A-Za-z0-9_]*"),
        ("OP",       r"==|!=|<=|>=|[+\-*/<>=!]"),
        ("LPAREN",   r"\("),
        ("RPAREN",   r"\)"),
        ("LBRACE",   r"\{"),
        ("RBRACE",   r"\}"),
        ("COMMA",    r","),
        ("SEMICOLON",r";"),
        ("NEWLINE",  r"\n"),
        ("SKIP",     r"[ \t\r]+"),
        ("MISMATCH", r"."),
    ]

    def __init__(self, code):
        self.code = code

    def tokenize(self):
        regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in self.TOKEN_SPEC)
        tokens = []
        line_num = 1
        line_start = 0
        for mo in re.finditer(regex, self.code):
            kind = mo.lastgroup
            value = mo.group()
            col = mo.start() - line_start + 1

            if kind == "NEWLINE":
                line_num += 1
                line_start = mo.end()
                continue
            if kind in ("SKIP", "COMMENT"):
                continue
            if kind == "MISMATCH":
                raise SyntaxError(f"Unexpected character {value!r} at {line_num}:{col}")

            if kind == "ID":
                ttype = self.KEYWORDS.get(value, "ID")
                if ttype == "TRUE":
                    tokens.append(Token("BOOLEAN", True, line_num, col))
                elif ttype == "FALSE":
                    tokens.append(Token("BOOLEAN", False, line_num, col))
                else:
                    tokens.append(Token(ttype, value, line_num, col))
            elif kind == "NUMBER":
                val = float(value) if "." in value else int(value)
                tokens.append(Token("NUMBER", val, line_num, col))
            elif kind == "STRING":
                # unescape quotes/newlines minimally
                if value[0] == '"':
                    inner = value[1:-1].encode('utf-8').decode('unicode_escape')
                else:
                    inner = value[1:-1].encode('utf-8').decode('unicode_escape')
                tokens.append(Token("STRING", inner, line_num, col))
            else:
                tokens.append(Token(kind, value, line_num, col))

        tokens.append(Token("EOF", None, line_num, 1))
        return tokens
