from .parse_string import parse_string

def parse_condition(current, to_parse):
    condition = { 'op': '' }

    if to_parse.match('!'):
        condition['op'] += '! '

    r = parse_string(to_parse)
    if r:
        condition['key'] = r

    elif to_parse.match('([a-zA-Z_0-9\\-\.:]+)'):
        condition['key'] = to_parse.match_group(1)

    else:
        raise Exception('parse condition: Can\'t parse condition key')

    if to_parse.match('(=~|!=|<|>|<=|>=|\^=|\$=|\*=|~=|=)'):
        condition['op'] += to_parse.match_group(1)
    else:
        condition['op'] += 'has_tag'

    r = parse_string(to_parse)
    if r:
        condition['value'] = r

        if not to_parse.match('\]'):
            raise Exception('parse condition: expecting ]')
    else:
        m = to_parse.match('([^\]]*)\]')
        condition['value'] = to_parse.match_group(1)

    if not 'conditions' in current:
        current['conditions'] = []

    current['conditions'].append(condition)
