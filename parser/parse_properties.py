from .parse_value import parse_value

def parse_properties(properties, to_parse):
    if not to_parse.match('\s*\{'):
        raise Exception('Error parsing, expecting {')

    while to_parse.to_parse():
        current = {}

        if to_parse.match('\s*([a-zA-Z0-9_\-]+)\s*:'):
            current['assignment_type'] = 'P'
            current['key'] = to_parse.match_group(1)

        elif to_parse.match('\s*set\s+([a-zA-Z0-9_\-\.]+)\s*='):
            current['assignment_type'] = 'T'
            current['key'] = to_parse.match_group(1)

        elif to_parse.match('\s*set\s+([a-zA-Z0-9_\-\.]+)\s*;'):
            current['assignment_type'] = 'T'
            current['key'] = to_parse.match_group(1)

            to_parse.rewind('yes;')

        elif to_parse.match('\s*unset\s+([a-zA-Z0-9_\-\.]+)\s*;'):
            current['assignment_type'] = 'T'
            current['key'] = to_parse.match_group(1)

            to_parse.rewind(';')

        elif to_parse.match('\s*combine\s+([a-zA-Z0-9_\-\.]+)\s+'):
            current['assignment_type'] = 'C'
            current['key'] = to_parse.match_group(1)

        else:
            raise Exception('Error parsing properties, expecing property or set statement')

        parse_value(current, to_parse)

        properties.append(current)

        if to_parse.match('\s*\}'):
            return

    return
