from .parse_string import parse_string
from .parse_eval import parse_eval
from .ParseError import *
import re

def parse_condition(to_parse):
    condition = { 'op': '', 'value_type': 'value' }
    pos = to_parse.pos()

    if to_parse.match('\s*!'):
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

    elif to_parse.match('\s*([a-zA-Z_0-9\\-\.:]+)'):
        condition['key'] = to_parse.match_group(1)

    elif to_parse.match('\s*\/([^\]]*)\/(i?)\]'):
        condition['op'] += 'key_regexp'
        condition['key'] = to_parse.match_group(1)

        if to_parse.match_group(2) == 'i':
            condition['op'] += '_case'

        return condition

    else:
        raise ParseError(to_parse, 'parse condition: Can\'t parse condition key')

    if to_parse.match('\s*(=~|!=|!~|<=|>=|<|>|\^=|\$=|\*=|~=|@=|=)\s*'):
        condition['op'] += to_parse.match_group(1)

    elif to_parse.match('\?\]'):
        condition['value'] = 'yes;true;1'
        condition['op'] += '@='
        return condition

    elif to_parse.match('\?\!\]'):
        condition['value'] = 'no;false;0;'
        condition['op'] += '@='
        return condition

    elif to_parse.match('\s*\]'):
        condition['op'] += 'has_tag'
        return condition

    else:
        # try to parse eval condition
        to_parse.seek(pos)

        value = parse_eval(to_parse, end_chars={']'})

        if not to_parse.match('\s*\]'):
            raise ParseError(to_parse, 'parse condition: Can\'t parse condition')

        condition['op'] = 'eval'
        condition['key'] = value

        return condition

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

    elif condition['op'] in ('=~', '!~'):
        condition['value'] = parse_string(to_parse, delim="/")

        m = to_parse.match('([^\]]*)\]')

        if m:
            condition['regexp_flags'] = to_parse.match_group(1)
        else:
            raise ParseError(to_parse, 'parse condition: expecting ]')

    else:
        m = to_parse.match('([^\]]*)\s*\]')
        if m:
            condition['value'] = to_parse.match_group(1)
        else:
            raise ParseError(to_parse, 'parse condition: expecting ]')

    return condition
