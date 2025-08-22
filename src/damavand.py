import re

class DamavandError(Exception):
    pass

class Damavand:
    def __init__(self):
        self.vars = {}

    def run(self, code):
        lines = code.splitlines()
        try:
            self._exec_block(lines, 0)
        except DamavandError as e:
            print(f"[Damavand Error] {e}")
        except Exception as e:
            print(f"[Damavand Error] {e}")

    def _exec_block(self, lines, i):
        n = len(lines)
        while i < n:
            raw = lines[i]
            line = raw.strip()

            if not line or line.startswith("#"):
                i += 1
                continue

            # var name = expr
            if line.startswith("var "):
                if "=" not in line[4:]:
                    raise DamavandError(f"Line {i+1}: expected '=' in variable declaration")
                name, expr = line[4:].split("=", 1)
                name = name.strip()
                if not name.isidentifier():
                    raise DamavandError(f"Line {i+1}: invalid variable name '{name}'")
                self.vars[name] = self.eval_expr(expr.strip())
                i += 1
                continue

            # print expr
            if line.startswith("print "):
                print(self.eval_expr(line[6:].strip()))
                i += 1
                continue

            # if condition { ... }
            if line.startswith("if "):
                header = line
                if "{" not in header:
                    raise DamavandError(f"Line {i+1}: expected '{{' after if condition")
                condition = header[3:header.index("{")].strip()
                block, i = self._collect_block(lines, i)
                if self.eval_expr(condition):
                    self._exec_block(block, 0)
                continue

            # while condition { ... }
            if line.startswith("while "):
                header = line
                if "{" not in header:
                    raise DamavandError(f"Line {i+1}: expected '{{' after while condition")
                condition = header[6:header.index("{")].strip()
                block, i = self._collect_block(lines, i)
                while self.eval_expr(condition):
                    self._exec_block(block, 0)
                continue

            # for init; cond; update { ... }
            if line.startswith("for "):
                header = line
                if "{" not in header:
                    raise DamavandError(f"Line {i+1}: expected '{{' after for header")
                header_inside = header[4:header.index("{")].strip()
                parts = [p.strip() for p in header_inside.split(";")]
                if len(parts) != 3:
                    raise DamavandError(f"Line {i+1}: for header must be 'init; condition; update'")
                init, cond, update = parts
                block, i = self._collect_block(lines, i)
                self._exec_single_stmt(init, i_hint=i+1)
                while self.eval_expr(cond):
                    self._exec_block(block, 0)
                    self._exec_single_stmt(update, i_hint=i+1)
                continue

            # simple assignment: name = expr
            if "=" in line and not any(line.startswith(k) for k in ("if ", "while ", "for ", "print ", "var ")):
                name, expr = line.split("=", 1)
                name = name.strip()
                if not name.isidentifier():
                    raise DamavandError(f"Line {i+1}: invalid assignment target '{name}'")
                self.vars[name] = self.eval_expr(expr.strip())
                i += 1
                continue

            # tolerate stray braces by skipping
            if line == "}":
                i += 1
                continue

            raise DamavandError(f"Line {i+1}: unknown command '{line}'")
        return i

    def _collect_block(self, lines, header_index):
        # header line contains "{"; return (block_lines, next_index_after_closing_brace)
        i = header_index + 1
        block = []
        n = len(lines)
        depth = 1
        while i < n and depth > 0:
            s = lines[i].strip()
            if s == "}":
                depth -= 1
                i += 1
                if depth == 0:
                    break
                else:
                    block.append(lines[i-1])
                    continue
            # simple nested support: count headers ending with "{"
            if "{" in s and s.endswith("{"):
                depth += 1
            block.append(lines[i])
            i += 1
        if depth != 0:
            raise DamavandError(f"Line {header_index+1}: missing '}}' to close block")
        return block, i

    def _exec_single_stmt(self, stmt, i_hint=0):
        s = stmt.strip()
        if not s:
            return
        if s.startswith("var "):
            if "=" not in s[4:]:
                raise DamavandError(f"Line {i_hint}: expected '=' in variable declaration")
            name, expr = s[4:].split("=", 1)
            name = name.strip()
            if not name.isidentifier():
                raise DamavandError(f"Line {i_hint}: invalid variable name '{name}'")
            self.vars[name] = self.eval_expr(expr.strip())
            return
        if s.startswith("print "):
            print(self.eval_expr(s[6:].strip()))
            return
        if "=" in s:
            name, expr = s.split("=", 1)
            name = name.strip()
            if not name.isidentifier():
                raise DamavandError(f"Line {i_hint}: invalid assignment target '{name}'")
            self.vars[name] = self.eval_expr(expr.strip())
            return
        raise DamavandError(f"Line {i_hint}: unsupported statement in this context: '{s}'")

    def eval_expr(self, expr):
        try:
            safe_globals = {"__builtins__": {}}
            expr2 = re.sub(r'\btrue\b', 'True', expr)
            expr2 = re.sub(r'\bfalse\b', 'False', expr2)
            return eval(expr2, safe_globals, dict(self.vars))
        except NameError as e:
            raise DamavandError(f"Undefined variable in expression '{expr}': {e}")
        except SyntaxError as e:
            raise DamavandError(f"Invalid expression '{expr}': {e.msg}")
        except Exception as e:
            expr_strip = expr.strip()
            if (expr_strip.startswith('"') and expr_strip.endswith('"')) or \
               (expr_strip.startswith("'") and expr_strip.endswith("'")):
                return expr_strip[1:-1]
            raise DamavandError(f"Error evaluating expression '{expr}': {e}")