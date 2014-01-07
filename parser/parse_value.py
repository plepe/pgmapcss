import re
from .parse_string import parse_string
from .parse_eval import parse_eval
from .ParseError import *

def parse_url(current, to_parse):
    if to_parse.match('\s*url\('):
        s = parse_string(to_parse)

        if s:
            if to_parse.match('\s*\)\s*;'):
                current['value'] = s
                current['value_type'] = 'url'
                return

        else:
            if to_parse.match('([^\)]*)\);'):
                current['value'] = to_parse.match_group(1)
                current['value_type'] = 'url'
                return
    else:
        if to_parse.match('\s*([^;]*);'):
            current['value'] = to_parse.match_group(1)
            current['value_type'] = 'url'
            return to_parse

def parse_value(current, to_parse):
    # strip prepending whitespace
    while True:
        if not to_parse.match('\s+'):
            break;

    # "..." or '...'
    s = parse_string(to_parse)
    if s is not None:
        if to_parse.match('\s*;'):
            current['value'] = s
            current['value_type'] = 'string'
            return

    # eval( ... )
    elif to_parse.match('eval\s*\(\s*'):
        r = parse_string(to_parse)
        if r:
            value = parse_eval(r)
        else:
            value = parse_eval(to_parse)

        if not to_parse.match('\s*\)\s*;'):
            raise ParseError(to_parse, 'Error parsing eval statement')

        current['value'] = value
        current['value_type'] = 'eval'
        return

    # rgb(R, G, B)
    elif to_parse.match('rgb\s*\(([0-9\.,%\s]+)\)\s*;'):
        values = to_parse.match_group(1).split(',')
        if len(values) != 3:
            raise ParseError(to_parse, 'Error parsing rgb() value: "' + v + '"')

        for i, v in enumerate(values):
            if re.match('\s*[0-9]+\s*$', v): # integer: 0..255
                values[i] = int(v)
                if values[i] < 0 or values[i] > 255:
                    raise ParseError(to_parse, 'Error parsing rgb() value, value {} out of range (0..255)'.format(v))

            elif re.match('\s*([0-9]+\.[0-9]+)\s*$', v): # float: 0.0..1.0
                values[i] = float(v)
                if values[i] < 0.0 or values[i] > 1.0:
                    raise ParseError(to_parse, 'Error parsing rgb() value, value {} out of range (0.0..1.0)'.format(v))
                values[i] = round(v * 255)

            elif re.match('\s*([0-9]+(\.[0-9]+)?)%\s*$', v): # percentage: 0%..100%
                m = re.match('\s*([0-9]+(\.[0-9]+)?)%\s*$', v)
                values[i] = float(m.group(1))
                print(values[i])
                if values[i] < 0.0 or values[i] > 100.0:
                    raise ParseError(to_parse, 'Error parsing rgb() value, value {} out of range (0%..100%)'.format(v))
                values[i] = round(values[i] * 2.55)

            else:
                raise ParseError(to_parse, 'Error parsing rgb() value, number format not detected: {}'.format(v))

        current['value'] = '#' + ''.join([ '%02x' % v for v in values ])
        current['value_type'] = 'rgb'
        return

    # url( ... )
    elif to_parse.match('url\s*\(', wind=None):
        return parse_url(current, to_parse)

    # else
    if to_parse.match('\s*([^;]*)\s*;'):
        current['value_type'] = 'value';
        current['value'] = to_parse.match_group(1).strip()

        m = re.match('(.*)(px|m|u)$', current['value'])
        if m:
            current['value'] = m.group(1)
            current['unit'] = m.group(2)

        if current['value'] == '':
            current['value'] = None

    return
