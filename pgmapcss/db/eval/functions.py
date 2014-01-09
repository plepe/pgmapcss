class Functions:
    def __init__(self):
        self.eval_functions = {}

    def list(self):
        return self.eval_functions

    def register(self, func, op=None, math_level=None, compiler=None):
        f = {}

        if func in self.eval_functions:
            f = self.eval_functions[func]

        if op:
            if type(op) == tuple:
                f['op'] = set( op )
            else:
                f['op'] = { op }

        if math_level:
            f['math_level'] = math_level

        if compiler:
            f['compiler'] = compiler

        self.eval_functions[func] = f
