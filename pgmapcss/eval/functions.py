class Functions:
    def __init__(self):
        self.eval_functions = {}

    def list(self):
        return self.eval_functions

    def print(self):
        ret = ''

        for func, f in self.eval_functions.items():
            if 'src' in f:
                ret += f['src']

        return ret


    def register(self, func, op=None, math_level=None, compiler=None, src=None):
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

        if src:
            f['src'] = src

        self.eval_functions[func] = f
