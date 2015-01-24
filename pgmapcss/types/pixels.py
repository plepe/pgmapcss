from .default import default
from ..compiler.compile_eval import compile_eval
import re
import copy

def float_to_str(v, default=None):
    r = repr(v)
    if r[-2:] == '.0':
        r = r[:-2]
    return r

class pixels(default):
    def _parse(self, value):
        if value is None:
            return None

        m = re.match('([\-\+]?[0-9]+(\.[0-9]+)?)(px|m|u)$', value)
        if m:
            return ( m.group(1), m.group(3) )

        m = re.match('([\-\+]?[0-9]+(\.[0-9]+)?)$', value)
        if m:
            return ( m.group(1), 'px' )

        return None


    def compile_postprocess(self):
        result = compile_eval([ 'o:+', [ 'f:prop', 'v:' + self.key, 'v:default' ], [ 'f:prop', 'v:' + self.key ]], { 'key': self.key }, self.stat)
        result['code'] = "if " + repr(self.key) + " in current['properties'][pseudo_element] and current['properties'][pseudo_element][" + repr(self.key) + "] is not None and len(current['properties'][pseudo_element][" + repr(self.key) + "]) > 0 and current['properties'][pseudo_element][" + repr(self.key) + "][0] == '+':\n" +\
               "    if pseudo_element != 'default':\n" +\
               "        current['properties'][pseudo_element][" + repr(self.key) + "] = " +\
               result['code'] + "\n" +\
               "    else:\n" +\
               "        current['properties'][pseudo_element][" + repr(self.key) + "] = " +\
               "current['properties'][pseudo_element][" + repr(self.key) + "][1:]"
        return result['code']

    def stat_postprocess(self, values, pseudo_element=None):
        ret = set()

        default_values = self.stat.property_values(self.key, pseudo_element='default', include_illegal_values=False, postprocess=False)

        if pseudo_element is None or pseudo_element == 'default':
            ret = ret.union({
                d[1:] if d[0] == '+' else d
                for d in default_values
            })

        if pseudo_element:
            pseudo_elements = { pseudo_element }
        else:
            pseudo_elements = copy.copy(self.stat['pseudo_elements'])
        if 'default' in pseudo_elements:
            pseudo_elements.remove('default')

        for p in pseudo_elements:
            p_values = self.stat.property_values(self.key, pseudo_element=p, include_illegal_values=False, postprocess=False)
            ret = ret.union({
                float_to_str(float(d) + float(v)) if v[0] == '+' else v
                for v in p_values
                for d in default_values
            })

        return ret

    def compile(self, prop):
        v = self._parse(prop['value'])

        if v is None:
            return None

        prefix = ''

        # relative value add from value on default layer; remember to add if value is evaluated from eval function
        if v[0][0] in ('+'):
            prefix = "'+' + "

        if v[1] == 'px':
            return repr(v[0])

        result = compile_eval([ 'f:metric', 'v:' + v[0] + v[1] ], prop, self.stat)

        return prefix + self.compile_check(result['code'])

    def stat_value(self, prop):
        v = self._parse(prop['value'])

        if v is None:
            return None

        if v[0] == '':
            return None

        if v[1] == 'px':
            return v[0]

        return True
