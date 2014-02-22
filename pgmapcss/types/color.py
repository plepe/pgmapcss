from .default import default
from pgmapcss.colors import to_color
from pgmapcss.compiler.CompileError import *

class color(default):
    def compile_check(self, value):
        return 'check_color(' + value + ')'

    def compile(self, prop):
        ret = to_color(prop['value'])
        if not ret:
            raise CompileError("Error: Unknown color '{}'".format(prop['value']))

        return repr(ret)

    def stat_value(self, prop):
        if not prop.get('value'):
            return None

        return to_color(prop['value'])

