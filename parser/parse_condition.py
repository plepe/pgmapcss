from .parse_string import parse_string
import re

def parse_condition(current, to_parse):
    condition = { 'op': '' }

    if re.match('!', to_parse):
        to_parse = to_parse[1:]
        condition['op'] += '! '

    r = parse_string(to_parse)
    if r[0]:
        condition['key'] = r[0]
        to_parse = r[1]

    elif re.match('([a-zA-Z_0-9\\-\.:]+)', to_parse):
        m = re.match('([a-zA-Z_0-9\\-\.:]+)', to_parse)
        condition['key'] = m.group(1)
        to_parse = to_parse[len(m.group(1)):]

    else:
        # TODO error?
        pass

    m = re.match('(=~|!=|<|>|<=|>=|\^=|\$=|\*=|~=|=)', to_parse)
    if m:
        condition['op'] += m.group(1)
        to_parse = to_parse[len(m.group(1)):]
    else:
        condition['op'] += 'has_tag'

    r = parse_string(to_parse)
    if r[0]:
        condition['value'] = r[0]
        to_parse = r[1]

        if not re.match('\]', to_parse):
            # TODO error
            pass
        else:
            to_parse = to_parse[1:]
    else:
        m = re.match('([^\]]*)\]', to_parse)
        condition['value'] = m.group(1)
        to_parse = to_parse[len(m.group(0)):]

    if not 'conditions' in current:
        current['conditions'] = []

    current['conditions'].append(condition)

    return to_parse
