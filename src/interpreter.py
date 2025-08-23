from .dam_ast import *

class RuntimeErrorEx(Exception):
    pass

class Interpreter:
    def __init__(self):
        self.globals = {}
        self.functions = {}

    def run(self, program: Program):
        for stmt in program.statements:
            self.exec_stmt(stmt)

    # --------------- statements ---------------
    def exec_stmt(self, node):
        if isinstance(node, FuncDef):
            self.functions[node.name] = node
        elif isinstance(node, Call):
            self._call(node)
        elif isinstance(node, If):
            if self.eval_expr(node.cond):
                for s in node.then_branch:
                    self.exec_stmt(s)
            else:
                for s in node.else_branch:
                    self.exec_stmt(s)
        elif isinstance(node, While):
            while self.eval_expr(node.cond):
                for s in node.body:
                    self.exec_stmt(s)
        elif isinstance(node, Print):
            print(self.eval_expr(node.expr))
        elif isinstance(node, Assign):
            self.globals[node.name] = self.eval_expr(node.expr)
        else:
            raise RuntimeErrorEx(f"Unknown statement {type(node)}")

    # --------------- expressions ---------------
    def eval_expr(self, node):
        if isinstance(node, Literal):
            return node.value
        if isinstance(node, Var):
            if node.name in self.globals:
                return self.globals[node.name]
            return None
        if isinstance(node, UnaryOp):
            v = self.eval_expr(node.expr)
            if node.op == "-": return -v
            if node.op == "!": return not v
            raise RuntimeErrorEx(f"Unknown unary {node.op}")
        if isinstance(node, BinaryOp):
            l = self.eval_expr(node.left)
            r = self.eval_expr(node.right)
            if node.op == "+":  return l + r
            if node.op == "-":  return l - r
            if node.op == "*":  return l * r
            if node.op == "/":  return l / r
            if node.op == "==": return l == r
            if node.op == "!=": return l != r
            if node.op == "<":  return l < r
            if node.op == ">":  return l > r
            if node.op == "<=": return l <= r
            if node.op == ">=": return l >= r
            raise RuntimeErrorEx(f"Unknown op {node.op}")
        if isinstance(node, Call):
            return self._call(node)
        raise RuntimeErrorEx(f"Unknown expr {type(node)}")

    def _call(self, node: Call):
        if node.name not in self.functions:
            raise RuntimeErrorEx(f"Undefined function {node.name}")
        fn = self.functions[node.name]
        if len(node.args) != len(fn.params):
            raise RuntimeErrorEx(f"Arg count mismatch for {node.name}")
        # bind params
        local = {p: self.eval_expr(a) for p, a in zip(fn.params, node.args)}
        # snapshot globals and execute body with local overlay
        saved = dict(self.globals)
        try:
            self.globals.update(local)
            for s in fn.body:
                self.exec_stmt(s)
        finally:
            self.globals = saved
