from .parse_value import *
from .strip_comments import strip_comments
import re

def parse_defines(stat, to_parse):
    while True:
        if not to_parse.match('\s*@([A-Za-z0-9_]*)\s+'):
            return

        define_type = to_parse.match_group(1)

        if define_type == 'import':
            current = {}
            parse_url(current, to_parse.to_parse())
            # to_parse = strip_comments(open(current['value']).read()) + to_parse

        else:
            if not to_parse.match('\s*([A-Za-z0-9_\-]*)\s+'):
                # TODO: error
                return

            if not define_type in stat['defines']:
                stat['defines'][define_type] = {}

            key = to_parse.match_group(1)
            current = {}
            parse_value(current, to_parse)

            stat['defines'][define_type][key] = current
