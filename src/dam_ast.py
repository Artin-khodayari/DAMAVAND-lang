class Program:
    def __init__(self, statements):
        self.statements = statements


class FuncDef:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body


class Call:
    def __init__(self, name, args):
        self.name = name
        self.args = args


class If:
    def __init__(self, cond, then_branch, else_branch):
        self.cond = cond
        self.then_branch = then_branch
        self.else_branch = else_branch


class While:
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body


class Print:
    def __init__(self, expr):
        self.expr = expr


class Assign:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr


class Var:
    def __init__(self, name):
        self.name = name


class Literal:
    def __init__(self, value):
        self.value = value


class BinaryOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class UnaryOp:
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr
