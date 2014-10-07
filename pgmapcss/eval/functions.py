from pkg_resources import *
from ..includes import *
from .base import config_base

class Functions:
    def __init__(self, stat):
        self.eval_functions = None
        self.eval_functions_source = {}
        self._eval = None
        self._eval_global_data = None
        self.stat = stat

    def list(self):
        if not self.eval_functions:
            self.resolve_config()

        return self.eval_functions

    def print(self, indent=''):
        ret = ''

        for func, src in self.eval_functions_source.items():
            ret += src

        if not self.stat or 'angular_system' not in self.stat['config'] or self.stat['config']['angular_system'] == 'degrees':
            ret = ret.replace("FROM_DEGREES", "")
            ret = ret.replace("FROM_RADIANS", "math.degrees")
            ret = ret.replace("TO_DEGREES", "")
            ret = ret.replace("TO_RADIANS", "math.radians")
        else:
            ret = ret.replace("FROM_DEGREES", "math.radians")
            ret = ret.replace("FROM_RADIANS", "")
            ret = ret.replace("TO_DEGREES", "math.degrees")
            ret = ret.replace("TO_RADIANS", "")

        # indent all lines
        ret = indent + ret.replace('\n', '\n' + indent)

        return ret


    def eval(self, statement, additional_code=''):
        if not 'global_data' in self.stat:
            self.stat['global_data'] = {}

        if repr(self.stat['global_data']) != self._eval_global_data:
            self._eval = None

        if not self._eval or additional_code != '':
            self._eval_global_data = repr(self.stat['global_data'])
            content = \
                'def _eval(statement):\n' +\
                '    import re\n' +\
                '    import math\n' +\
                '    global_data = ' + repr(self.stat['global_data']) + '\n' +\
                '    ' + resource_string(__name__, 'base.py').decode('utf-8').replace('\n', '\n    ') +\
                '\n' +\
                '    ' + include_text().replace('\n', '\n    ') +\
                '\n' +\
                additional_code.replace('\n', '\n    ') +\
                '\n' +\
                self.print(indent='    ') + '\n'\
                '    return eval(statement)'

            eval_code = compile(content, '<eval functions>', 'exec')
            eval_ns = {}
            exec(eval_code, eval_ns, eval_ns);

            _eval = eval_ns['_eval']
            if additional_code == '':
                self._eval = _eval

        else:
            _eval = self._eval

        return _eval(statement)

    def resolve_config(self):
        exec(
            resource_string(__name__, 'base.py').decode('utf-8') +
            self.print()
        )

        self.eval_functions = {}
        self.aliases = {}
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

            if config.aliases is not None:
                for a in config.aliases:
                    self.aliases[a] = func

            self.eval_functions[func] = config

    def register(self, func, src):
        self.eval_functions_source[func] = src

    def call(self, func, param, stat):
        import re
        import pgmapcss.db as db
        config = self.eval_functions[func]

        statement = config.compiler([ repr(p) for p in param ], '', stat)
        return self.eval(statement)

    def test(self, func, src):
        print('* Testing %s' % func)

        import re
        import pgmapcss.db as db
        rows = src.split('\n')
        config = self.eval_functions[func]

        ret = '''
create or replace function __eval_test__() returns text
as $body$
import re
import math
''' +\
resource_string(__name__, 'base.py').decode('utf-8') +\
include_text() +\
'''
global_data = {'icon-image': {'crossing.svg': (11, 7)}}
parameters = {'lang': 'en', 'foo': 'bar'}
current = { 'object': { 'id': 'n123', 'tags': { 'amenity': 'restaurant', 'name': 'Foobar', 'name:en': 'English Foobar', 'cuisine': 'pizza;kebab;noodles' }}, 'pseudo_element': 'default', 'pseudo_elements': ['default', 'test'], 'tags': { 'amenity': 'restaurant', 'name': 'Foobar', 'cuisine': 'pizza;kebab;noodles' }, 'properties': { 'default': { 'width': '2', 'color': '#ff0000' }, 'test': { 'fill-color': '#00ff00', 'icon-image': 'crossing.svg', 'text': 'Test' } } }
render_context = {'bbox': '010300002031BF0D000100000005000000DBF1839BB5DC3B41E708549B2B705741DBF1839BB5DC3B41118E9739B171574182069214CCE23B41118E9739B171574182069214CCE23B41E708549B2B705741DBF1839BB5DC3B41E708549B2B705741', 'scale_denominator': 8536.77}
'''
        ret += self.print()
        ret += "result = ''\n"

        param_in = None
        for r in rows:
            m = re.match('# IN (.*)$', r)
            if m:
                param_in = eval(m.group(1))

            m = re.match('# OUT(_ROUND)? (.*)$', r)
            if m:
                return_out = eval(m.group(2))
                shall_round = m.group(1) == '_ROUND'

                ret += 'ret = ' + config.compiler([ repr(p) for p in param_in ], '', {}) + '\n'
                ret += 'result += "IN  %s\\n"\n' % repr(param_in)
                ret += 'result += "EXP %s\\n"\n' % repr(return_out)
                ret += 'result += "OUT %s\\n" % repr(ret)\n'

                ret += 'if type(ret) != str:\n    result += "ERROR not a string: " + repr(ret) + "\\n"\n'
                if shall_round:
                    ret += 'elif round(float(ret), 5) != %s:\n    result += "ERROR return value wrong!\\n"\n' % repr(round(float(return_out), 5))
                else:
                    ret += 'elif ret != %s:\n    result += "ERROR return value wrong!\\n"\n' % repr(return_out)

        ret += 'return result\n'
        ret += "$body$ language 'plpython3u' immutable;"
        #print(ret)
        conn = db.connection()
        conn.execute(ret)

        r = conn.prepare('select __eval_test__()');
        res = r()[0][0]

        print(res)

        if(re.search("^ERROR", res, re.MULTILINE)):
            raise Exception("eval-test failed!")

    def test_all(self):
        if not self.eval_functions:
            self.resolve_config()

        [ self.test(func, src) for func, src in self.eval_functions_source.items() ]
