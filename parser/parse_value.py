import re
from .parse_string import parse_string

def parse_url(current, to_parse):
    m = re.match('\s*url\(', to_parse)
    if m:
        to_parse = to_parse[len(m.group(0)):]
        s = parse_string(to_parse)

        if s[0]:
            to_parse = to_parse[len(s[2]):]
            m1 = re.match('\s*\)\s*;', to_parse)
            if m1:
                to_parse = to_parse[len(m1.group(0)):]
                current['value'] = s[0]
                current['value_type'] = 'url'
                return to_parse

        else:
            m1 = re.match('([^\)]*)\);', to_parse)
            if m1:
                to_parse = to_parse[len(m1.group(0)):]
                current['value'] = m.group(1)
                current['value_type'] = 'url'
                return to_parse
    else:
        m = re.match('\s*([^;]*);', to_parse)
        if m:
            to_parse = to_parse[len(m.group(0)):]
            current['value'] = m.group(1)
            current['value_type'] = 'url'
            return to_parse

def parse_value(current, to_parse):
    # strip prepending whitespace
    while True:
        m = re.match('\s+', to_parse)
        if not m:
            break;

        to_parse = to_parse[len(m.group(0)):]

    # "..." or '...'
    s = parse_string(to_parse)
    if s[0] is not None:
        m = re.match('\s*;', s[1])
        if m:
            current['value'] = s[0]
            current['value_type'] = 'string'
            return s[1][len(m.group(0)):]

    # eval( ... )
    elif re.match('eval\s*\(', to_parse):
        # TODO
        m = re.match('eval\s*\((.*)\)\s*;', to_parse)
        if m:
            current['value'] = m.group(1)
            current['value_type'] = 'eval'
            return to_parse[len(m.group(0)):]
        pass

    # rgb(R, G, B)
    elif re.match('rgb\s*\(', to_parse):
        # TODO
        m = re.match('rgb\s*\((.*)\)\s*;', to_parse)
        if m:
            current['value'] = m.group(1)
            current['value_type'] = 'rgb'
            return to_parse[len(m.group(0)):]
        pass

    # url( ... )
    elif re.match('url\s*\(', to_parse):
        return parse_url(current, to_parse)

    # else
    if re.match('\s*([^;]*)\s*;', to_parse):
        m = re.match('\s*([^;]*)\s*;', to_parse)
        current['value_type'] = 'value';
        current['value'] = m.group(1)

        if current['value'] == '':
            current['value'] = None

        to_parse = to_parse[len(m.group(0)):]

    return to_parse
