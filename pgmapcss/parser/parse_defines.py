from .parse_value import *
from .strip_comments import strip_comments
from .check_media_query import *
import re

def parse_defines(stat, to_parse):
    while True:
        if not to_parse.match('\s*@([A-Za-z0-9_]*)\s+'):
            return

        define_type = to_parse.match_group(1)

        if define_type == 'import':
            current = {}
            parse_url(current, to_parse)

            if not to_parse.match('\s*;'):
                raise ParseError(to_parse, 'Error parsing @import statement, expecing ";" or "}"')

            return ( 'import', current['value'] )

        elif define_type == 'media':
            query = [ [ '' ] ]

            last_to_parse = None
            parse_mode = 0
            while True:
                if to_parse.pos() == last_to_parse:
                    raise ParseError(to_parse, 'Error parsing @media query at')

                last_to_parse = to_parse.pos()

                if parse_mode == 0:
                    if to_parse.match('\s*(not)'):
                        query[-1][0] = 'NOT'

                    parse_mode = 1

                if parse_mode == 1:
                    if to_parse.match('\s*([a-zA-Z\-0-9]+)'):
                        query[-1].append((
                            'type',
                            to_parse.match_group(1)
                        ))
                        parse_mode = 2

                    elif to_parse.match('\s*\(\s*([a-zA-Z\-0-9]+)\s*(:\s*([^\)]+))?\s*\)'):
                        query[-1].append((
                            to_parse.match_group(1),
                            to_parse.match_group(3)
                        ))
                        parse_mode = 2

                    else:
                        raise ParseError(to_parse, 'Error parsing @media query, expecting feature or type query')

                if parse_mode == 2:
                    if to_parse.match('\s*({|and|,)'):
                        if len(query[-1]) < 2:
                            raise ParseError(to_parse, 'Error parsing @media query, need at least one media type or feature query')

                        elif to_parse.match_group(1) == '{':
                            return check_media_query(stat, to_parse, query)

                        elif to_parse.match_group(1) == 'and':
                            parse_mode = 1

                        elif to_parse.match_group(1) == ',':
                            query.append([ '' ])
                            parse_mode = 0
                    else:
                        raise ParseError(to_parse, 'Error parsing @media query, expecting "{", "and" or ","')

        elif define_type == 'config':
            if not to_parse.match('\s*([A-Za-z0-9_\-]*)\s+'):
                # TODO: error
                return

            key = to_parse.match_group(1)
            current = {}
            parse_value(current, to_parse)

            stat['config'][key] = current['value']

            if not to_parse.match('\s*;'):
                raise ParseError(to_parse, 'Error parsing config option, expecing ;')

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
