from pkg_resources import *
from ..includes import *
from .base import config_base

class Functions:
    def __init__(self):
        self.eval_functions = None
        self.eval_functions_source = {}

    def list(self):
        if not self.eval_functions:
            self.resolve_config()

        return self.eval_functions

    def print(self, indent=''):
        ret = ''

        for func, src in self.eval_functions_source.items():
            ret += src

        # indent all lines
        ret = indent + ret.replace('\n', '\n' + indent)

        return ret


    def resolve_config(self):
        exec(
            resource_string(__name__, 'base.py').decode('utf-8') +
            self.print()
        )

        self.eval_functions = {}
        for func, src in self.eval_functions_source.items():
            if 'config_eval_' + func in locals():
                config = locals()['config_eval_' + func](func)
            else:
                config = config_base(func)

            if config.op is None:
                config.op = set()
            elif type(config.op) == tuple:
                config.op = set( config.op )
            else:
                config.op = { config.op }

            self.eval_functions[func] = config

    def register(self, func, src):
        self.eval_functions_source[func] = src

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
''' +\
resource_string(__name__, 'base.py').decode('utf-8') +\
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
