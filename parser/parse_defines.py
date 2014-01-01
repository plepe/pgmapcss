from .parse_value import *
from .strip_comments import strip_comments
import re

def parse_defines(stat, to_parse):
    while True:
        m = re.match('\s*@([A-Za-z0-9_]*)\s+', to_parse)
        if not m:
            return to_parse

        define_type = m.group(1)
        to_parse = to_parse[len(m.group(0)):]

        if define_type == 'import':
            current = {}
            to_parse = parse_url(current, to_parse)
            to_parse = strip_comments(open(current['value']).read()) + to_parse

        else:
            m = re.match('\s*([A-Za-z0-9_\-]*)\s+', to_parse)

            if not m:
                # TODO: error
                return to_parse

            if not define_type in stat['defines']:
                stat['defines'][define_type] = {}

            to_parse = to_parse[len(m.group(0)):]

            current = {}
            to_parse = parse_value(current, to_parse)

            stat['defines'][define_type][m.group(1)] = current

    return to_parse
