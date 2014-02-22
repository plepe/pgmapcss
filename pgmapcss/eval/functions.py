from pkg_resources import *
from ..includes import *

class Functions:
    def __init__(self):
        self.eval_functions = {}

    def list(self):
        return self.eval_functions

    def print(self, indent=''):
        ret = ''

        for func, f in self.eval_functions.items():
            if 'src' in f:
                ret += f['src']

        # indent all lines
        ret = indent + ret.replace('\n', '\n' + indent)

        return ret


    def register(self, func, op=None, math_level=None, compiler=None, src=None, unary=False):
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

        if src:
            f['src'] = src

        self.eval_functions[func] = f

    def test(self, func, conf):
        print('* Testing %s' % func)

        if 'src' not in conf:
            return

        import re
        import pgmapcss.db as db
        rows = conf['src'].split('\n')

        ret = '''
create or replace function __eval_test__(param text[]) returns text
as $body$
import re
def to_float(v, default=None):
    try:
        return float(v)
    except ValueError:
        return default
def to_int(v, default=None):
    try:
        return int(v)
    except ValueError:
        return default
def float_to_str(v, default=None):
    r = repr(v)
    if r[-2:] == '.0':
        r = r[:-2]
    return r
''' +\
include_text() +\
'''
current = { 'object': { 'id': 'n123', 'tags': { 'amenity': 'restaurant', 'name': 'Foobar', 'cuisine': 'pizza;kebab;noodles' }}, 'pseudo_element': 'default', 'pseudo_elements': ['default', 'test'], 'tags': { 'amenity': 'restaurant', 'name': 'Foobar', 'cuisine': 'pizza;kebab;noodles' }, 'properties': { 'default': { 'width': '2', 'color': '#ff0000' }, 'test': { 'fill-color': '#00ff00' } } }
render_context = {'bbox': '010300002031BF0D000100000005000000DBF1839BB5DC3B41E708549B2B705741DBF1839BB5DC3B41118E9739B171574182069214CCE23B41118E9739B171574182069214CCE23B41E708549B2B705741DBF1839BB5DC3B41E708549B2B705741', 'scale_denominator': 8536.77}
'''
        ret += self.print()
        ret += 'ret = eval_' + func + '(param)\n'
        ret += 'if type(ret) != str:\n    return "not a string: " + repr(ret)\n'
        ret += 'return ret\n'
        ret += "$body$ language 'plpython3u' immutable;"
        conn = db.connection()
        conn.execute(ret)

        param_in = None
        for r in rows:
            m = re.match('# IN (.*)$', r)
            if m:
                param_in = eval(m.group(1))

            m = re.match('# OUT (.*)$', r)
            if m:
                return_out = eval(m.group(1))

                r = conn.prepare('select __eval_test__($1)');
                res = r(param_in)

                print(' IN  %s' % repr(param_in))
                print(' EXP %s' % repr(return_out))
                print(' OUT %s' % repr(res[0][0]))

                if repr(return_out) != repr(res[0][0]):
                    raise Exception("eval-test failed!")

    def test_all(self):
        [ self.test(func, conf) for func, conf in self.eval_functions.items() ]
