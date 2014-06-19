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
            parse_url(current, to_parse)
            return ( 'import', current['value'] )

        elif define_type == 'media':
            query = [ [] ]

            last_to_parse = None
            while True:
                if to_parse.pos() == last_to_parse:
                    raise ParseError(to_parse, 'Error parsing @media query at')

                last_to_parse = to_parse.pos()

                if to_parse.match('\s*{'):
                    return ( 'media', query )

                elif to_parse.match('\s*(not)?\s*\(\s*([a-zA-Z\-0-9]+)\s*(:\s*(\w+))?\s*\)'):
                    query[-1].append((
                        to_parse.match_group(2),
                        to_parse.match_group(4),
                        to_parse.match_group(1))
                    )

                    if to_parse.match('\s*and\s*'):
                        pass
                    elif to_parse.match('\s*,\s*'):
                        query.append([])

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

            if not to_parse.match('\s*;'):
                raise ParseError(to_parse, 'Error parsing define, expecing ;')
