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
