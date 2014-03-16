from .default import default
from ..compiler.compile_eval import compile_eval
import re

class pixels(default):
    def _parse(self, value):
        if value is None:
            return None

        m = re.match('(\-?[0-9]+(\.[0-9]+)?)(px|m|u)$', value)
        if m:
            return ( m.group(1), m.group(3) )

        m = re.match('(\-?[0-9]+(\.[0-9]+)?)$', value)
        if m:
            return ( m.group(1), 'px' )

        return None


    def compile(self, prop):
        v = self._parse(prop['value'])

        if v is None:
            return None

        if v[1] == 'px':
            return repr(v[0])

        return self.compile_check(compile_eval([ 'f:metric', 'v:' + v[0] + v[1] ], self.stat))

    def stat_value(self, prop):
        v = self._parse(prop['value'])

        if v is None:
            return None

        if v[0] == '':
            return None

        if v[1] == 'px':
            return v[0]

        return True
