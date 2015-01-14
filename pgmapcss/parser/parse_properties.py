from .parse_value import parse_value
from .ParseError import *

def parse_properties(properties, to_parse, global_context=False, accept_assignment_types={'P', 'T', 'U', 'C', 'V'}):
    if not global_context and not to_parse.match('\s*\{'):
        raise ParseError(to_parse, 'Error parsing, expecting {')

    while to_parse.to_parse():
        current = {}

        if 'P' in accept_assignment_types and to_parse.match('\s*([a-zA-Z0-9_\-]+)\s*:'):
            current['assignment_type'] = 'P'
            current['key'] = to_parse.match_group(1)

        elif 'T' in accept_assignment_types and to_parse.match('\s*set\s+([a-zA-Z0-9_\-\.]+)\s*='):
            current['assignment_type'] = 'T'
            current['key'] = to_parse.match_group(1)

        elif 'T' in accept_assignment_types and to_parse.match('\s*set\s+([a-zA-Z0-9_\-\.]+)\s*(;|})'):
            current['assignment_type'] = 'T'
            current['key'] = to_parse.match_group(1)

            to_parse.rewind('yes' + to_parse.match_group(2))

        elif 'U' in accept_assignment_types and to_parse.match('\s*unset\s+([a-zA-Z0-9_\-\.]+)\s*(;|})'):
            current['assignment_type'] = 'U'
            current['key'] = to_parse.match_group(1)

            to_parse.rewind(to_parse.match_group(2))

        elif 'C' in accept_assignment_types and to_parse.match('\s*combine\s+([a-zA-Z0-9_\-\.]+)\s+'):
            current['assignment_type'] = 'C'
            current['key'] = to_parse.match_group(1)

        elif 'V' in accept_assignment_types and to_parse.match('\s*@([a-zA-Z0-9_]+)\s*:'):
            current['assignment_type'] = 'V'
            current['key'] = to_parse.match_group(1)

        elif to_parse.match('\s*\}'):
            return

        else:
            if global_context:
                return current
            else:
                raise ParseError(to_parse, 'Error parsing properties, expecing property or set statement')

        parse_value(current, to_parse)

        properties.append(current)

        if to_parse.match('\s*(;|})', wind=None):
            if to_parse.match_group(1) == ';':
                to_parse.wind(len(to_parse.match_group(0)))

        else:
            raise ParseError(to_parse, 'Error parsing properties, expecing ; or }')

    return
