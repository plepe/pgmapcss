class Functions:
    def __init__(self):
        self.eval_functions = {}

    def list(self):
        return self.eval_functions

    def register(self, func, op=None, math_level=None, compiler=None, unary=False):
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

        # only change unary when operation has been passed
        if op:
            f['unary'] = unary

        self.eval_functions[func] = f
