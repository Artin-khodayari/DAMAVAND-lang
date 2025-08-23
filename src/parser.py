from .dam_ast import (
    Program, FuncDef, Call, If, While, Print, Assign,
    Var, Literal, BinaryOp, UnaryOp
)

class ParserError(Exception):
    pass


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def cur(self):
        return self.tokens[self.pos]

    def eat(self, type_):
        tok = self.cur()
        if tok.type != type_:
            raise ParserError(f"Expected {type_}, got {tok.type} at {tok.line}:{tok.col}")
        self.pos += 1
        return tok

    def match(self, *types):
        if self.cur().type in types:
            t = self.cur()
            self.pos += 1
            return t
        return None

    def parse(self):
        stmts = []
        while self.cur().type != "EOF":
            stmts.append(self.statement())
        return Program(stmts)

    # ---------------- Statements ----------------
    def statement(self):
        t = self.cur()
        if t.type == "FFF":
            return self.func_def()
        if t.type == "IF":
            return self.if_stmt()
        if t.type == "WHILE":
            return self.while_stmt()
        if t.type == "PRINT":
            return self.print_stmt()
        if t.type == "ID":
            return self.assignment_or_call()
        raise ParserError(f"Unexpected token {t} at {t.line}:{t.col}")

    def func_def(self):
        self.eat("FFF")
        name = self.eat("ID").value
        self.eat("LPAREN")
        params = []
        if self.cur().type != "RPAREN":
            params.append(self.eat("ID").value)
            while self.match("COMMA"):
                params.append(self.eat("ID").value)
        self.eat("RPAREN")
        self.eat("LBRACE")
        body = []
        while self.cur().type != "RBRACE":
            body.append(self.statement())
        self.eat("RBRACE")
        return FuncDef(name, params, body)

    def if_stmt(self):
        self.eat("IF")
        self.eat("LPAREN")
        cond = self.expr()
        self.eat("RPAREN")
        then_body = self.block()
        else_body = []
        if self.match("ELSE"):
            else_body = self.block()
        return If(cond, then_body, else_body)

    def while_stmt(self):
        self.eat("WHILE")
        self.eat("LPAREN")
        cond = self.expr()
        self.eat("RPAREN")
        body = self.block()
        return While(cond, body)

    def print_stmt(self):
        self.eat("PRINT")
        value = self.expr()
        return Print(value)

    def assignment_or_call(self):
        name = self.eat("ID").value
        if self.cur().type == "OP" and self.cur().value == "=":
            self.eat("OP")
            value = self.expr()
            return Assign(name, value)
        if self.cur().type == "LPAREN":
            args = self.arguments()
            return Call(name, args)
        raise ParserError(f"Expected '=' or '(' after identifier at {self.cur().line}:{self.cur().col}")

    def arguments(self):
        self.eat("LPAREN")
        args = []
        if self.cur().type != "RPAREN":
            args.append(self.expr())
            while self.match("COMMA"):
                args.append(self.expr())
        self.eat("RPAREN")
        return args

    def block(self):
        self.eat("LBRACE")
        stmts = []
        while self.cur().type != "RBRACE":
            stmts.append(self.statement())
        self.eat("RBRACE")
        return stmts

    # ---------------- Expressions ----------------
    def expr(self):
        return self.equality()

    def equality(self):
        node = self.comparison()
        while self.cur().type == "OP" and self.cur().value in ("==", "!="):
            op = self.eat("OP").value
            right = self.comparison()
            node = BinaryOp(node, op, right)
        return node

    def comparison(self):
        node = self.term()
        while self.cur().type == "OP" and self.cur().value in ("<", ">", "<=", ">="):
            op = self.eat("OP").value
            right = self.term()
            node = BinaryOp(node, op, right)
        return node

    def term(self):
        node = self.factor()
        while self.cur().type == "OP" and self.cur().value in ("+", "-"):
            op = self.eat("OP").value
            right = self.factor()
            node = BinaryOp(node, op, right)
        return node

    def factor(self):
        node = self.unary()
        while self.cur().type == "OP" and self.cur().value in ("*", "/"):
            op = self.eat("OP").value
            right = self.unary()
            node = BinaryOp(node, op, right)
        return node

    def unary(self):
        tok = self.cur()
        if tok.type == "OP" and tok.value in ("-", "!"):
            op = self.eat("OP").value
            right = self.unary()
            return UnaryOp(op, right)
        return self.primary()

    def primary(self):
        tok = self.cur()
        if tok.type == "NUMBER":
            return Literal(self.eat("NUMBER").value)
        if tok.type == "STRING":
            return Literal(self.eat("STRING").value)
        if tok.type == "BOOLEAN":
            return Literal(self.eat("BOOLEAN").value)
        if tok.type == "ID":
            return Var(self.eat("ID").value)
        if tok.type == "LPAREN":
            self.eat("LPAREN")
            node = self.expr()
            self.eat("RPAREN")
            return node
        raise ParserError(f"Unexpected token {tok} at {tok.line}:{tok.col}")
