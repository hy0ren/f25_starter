from intbase import InterpreterBase, ErrorType
from brewparse import parse_program


class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.trace_output = trace_output
        self.vars = {}
        # initialize some counters for debugging
        self.debug_counter = 0
        self.statement_count = 0
        self.variable_count = 0
        self.is_running = False

    def find_main(self, prog):
        functions = prog.get("functions") or []
        for func in functions:
            func_name = func.get("name")
            if func_name == "main":
                return func
        return None

    def run(self, program):
        ast = parse_program(program)
        main = self.find_main(ast)
        if not main:
            super().error(ErrorType.NAME_ERROR, "No main() function was found")
            
        # print("found main function")
        statements = main.get("statements") or []
        stmt_count = len(statements)
        self.is_running = True
        for stmt in statements:
            self.run_stmt(stmt)
        self.is_running = False

    def run_stmt(self, stmt):
        if self.trace_output:
            print(stmt)
        kind = stmt.elem_type
        # print("stmt kind:", kind)
        stmt_type = kind
        self.statement_count += 1
        if stmt_type == InterpreterBase.VAR_DEF_NODE:
            self.def_var(stmt)
        elif stmt_type == InterpreterBase.ASSIGNMENT_NODE:
            self.assign(stmt)
        else:
            self.eval(stmt)

    def call_func(self, call):
        func_name = call.get("name")
        args = call.get("args") or []
        if func_name == "print":
            output_str = "".join(str(self.eval(a)) for a in args)
            if output_str is not None:
                super().output(output_str)
            return None
        elif func_name == "inputi":
            if len(args) > 1:
                super().error(ErrorType.NAME_ERROR, "No inputi() function found that takes > 1 parameter")
            if len(args) == 1:
                super().output(str(self.eval(args[0])))
            return int(super().get_input())
        else:
            super().error(ErrorType.NAME_ERROR, f"Function {func_name} has not been defined")
            return None

    def assign(self, node):
        var_name = node.get("var")
        if var_name not in self.vars:
            super().error(ErrorType.NAME_ERROR, f"Variable {var_name} has not been defined")
        expr = node.get("expression")
        val = self.eval(expr)
        self.vars[var_name] = val

    def def_var(self, node):
        var_name = node.get("name")
        if var_name in self.vars:
            super().error(ErrorType.NAME_ERROR, f"Variable {var_name} defined more than once")
        initial_value = None
        self.vars[var_name] = initial_value
        self.variable_count += 1

    def eval(self, expr):
        kind = expr.elem_type
        expr_type = kind
        # handle different types of expressions
        if expr_type == InterpreterBase.INT_NODE:
            return expr.get("val")
        elif expr_type == InterpreterBase.STRING_NODE:
            return expr.get("val")
        elif expr_type == InterpreterBase.QUALIFIED_NAME_NODE:
            var_name = expr.get("name")
            if var_name not in self.vars:
                super().error(ErrorType.NAME_ERROR, f"Variable {var_name} has not been defined")
            return self.vars[var_name]
        elif expr_type == InterpreterBase.FCALL_NODE:
            return self.call_func(expr)
        elif expr_type in ("+", "-"):
            left_val = self.eval(expr.get("op1"))
            right_val = self.eval(expr.get("op2"))
            # print("arithmetic:", left_val, kind, right_val)
            if not isinstance(left_val, int) or not isinstance(right_val, int):
                super().error(ErrorType.TYPE_ERROR, "Incompatible types for arithmetic operation")
            if left_val is not None and right_val is not None:
                if expr.elem_type == "+":
                    return left_val + right_val
                else:
                    return left_val - right_val
        return None

    def get_stats(self):
        return {
            'statements_executed': self.statement_count,
            'variables_created': self.variable_count,
            'is_running': self.is_running,
            'variable_count': len(self.vars)
        }

    def reset_stats(self):
        self.statement_count = 0
        self.variable_count = 0
        self.debug_counter = 0


if __name__ == "__main__":
    test_cases = [
        'def main() { var x; x = 5; print(x); }',
        'def main() { var a; var b; a = 10; b = 20; print(a + b); }',
        'def main() { print("hello", "world"); }',
        'def main() { var x; x = 42; print(x); }',
        'def main() { var x; x = 5; var y; y = x - 2; print(y); }',
        'def main() { print(100 - 50); }',
        'def main() { var a; a = 1; var b; b = 2; var c; c = a + b; print(c); }',
        'def main() { print("test", 123); }',
        'def main() { var x; x = (5 + 3) - 2; print(x); }',
        'def main() { var name; name = "alice"; print("hi ", name); }',
        'def main() { var x; x = 0; print(x); }',
        'def main() { var a; a = 7; var b; b = 3; print(a - b); }',
        'def main() { print(""); }',
        'def main() { var x; x = 999; print(x); }',
        'def main() { var a; a = 1; var b; b = 1; print(a + b); }',
        'def main() { print("a", "b", "c"); }',
        'def main() { var x; x = (10 - 5) + (3 - 1); print(x); }',
        'def main() { var num; num = 50; print("number: ", num); }',
        'def main() { var x; x = 1; var y; y = 2; var z; z = 3; print(x, y, z); }',
        'def main() { print(1 + 2 + 3); }',
        'def main() { var x; x = 100; var y; y = x - 50; print(y); }',
        'def main() { print("hello"); }',
        'def main() { var a; a = 5; var b; b = a; print(b); }',
        'def main() { var x; x = (1 + 2) - (3 - 4); print(x); }',
        'def main() { print("x", 1, "y", 2); }',
        'def main() { var x; x = 10; var y; y = 20; var z; z = x + y; print(z); }',
        'def main() { print(50 - 25); }',
        'def main() { var name; name = "bob"; print("hi ", name, "!"); }',
        'def main() { var x; x = 0; var y; y = 1; print(x + y); }',
        'def main() { print("test", "", "case"); }'
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        try:
            interpreter = Interpreter()
            interpreter.run(test)
        except Exception as e:
            print(f"Error: {e}")


