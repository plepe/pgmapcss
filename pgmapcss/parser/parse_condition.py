from .parse_string import parse_string
from .parse_eval import parse_eval
from .ParseError import *

def parse_condition(to_parse):
    condition = { 'op': '', 'value_type': 'value' }

    if to_parse.match('!'):
        condition['op'] += '! '

    r = parse_string(to_parse)
    if r:
        condition['key'] = r

    elif to_parse.match('eval\s*\(\s*'):
        value = parse_eval(to_parse)

        if not to_parse.match('\s*\)\s*\]'):
            raise ParseError(to_parse, 'Error parsing eval statement')

        condition['op'] = 'eval'
        condition['key'] = value

        return condition

    elif to_parse.match('([a-zA-Z_0-9\\-\.:]+)'):
        condition['key'] = to_parse.match_group(1)

    else:
        raise ParseError(to_parse, 'parse condition: Can\'t parse condition key')

    if to_parse.match('(=~|!=|<=|>=|<|>|\^=|\$=|\*=|~=|=)'):
        condition['op'] += to_parse.match_group(1)
    else:
        condition['op'] += 'has_tag'

    r = parse_string(to_parse)
    if r:
        condition['value'] = r

        if not to_parse.match('\]'):
            raise ParseError(to_parse, 'parse condition: expecting ]')

    elif to_parse.match('eval\s*\(\s*'):
        r = parse_string(to_parse)
        if r:
            value = parse_eval(r)
        else:
            value = parse_eval(to_parse)

        if not to_parse.match('\s*\)\s*\]'):
            raise ParseError(to_parse, 'Error parsing eval statement')

        condition['value'] = value
        condition['value_type'] = 'eval'

    elif to_parse.match('([0-9\.]+)(px|m|u)\s*]'):
        if to_parse.match_group(2) == 'px':
            condition['value'] = to_parse.match_group(1)
        else:
            condition['value'] = [ 'f:metric', 'v:' + to_parse.match_group(1) + to_parse.match_group(2) ]
            condition['value_type'] = 'eval'

    else:
        m = to_parse.match('([^\]]*)\]')
        if m:
            condition['value'] = to_parse.match_group(1)
        else:
            raise ParseError(to_parse, 'parse condition: expecting ]')

    return condition
