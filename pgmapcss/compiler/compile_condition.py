import pgmapcss.db as db
import re
from .compile_eval import compile_eval

def compile_condition(condition, stat, prefix='current.', var="current['tags']"):
    ret = ''
    final_value = None

    if 'value_type' in condition and condition['value_type'] == 'eval':
        final_value = compile_eval(condition['value'])

    elif 'value' in condition:
        final_value = repr(condition['value'])

    key = repr(condition['key'])

    # !
    if condition['op'][0:2] == '! ':
        ret += 'not '
        condition['op'] = condition['op'][2:]

    # has_tag
    if condition['op'] == 'has_tag':
        ret += key + ' in ' + var

    # =
    elif condition['op'] == '=':
        ret += var + '[' + key + "] == " + final_value

    # !=
    elif condition['op'] == '!=':
        ret += var + '[' + key + "] != " + final_value

    # < > <= >=
    elif condition['op'] in ('<', '>', '<=', '>='):
        ret += 'to_float(' + var + '[' + key + ']) ' + condition['op'] + ' to_float(' + final_value + ')';

    # ^=
    elif condition['op'] == '^=':
        ret += var + '[' + key + '].find(' + final_value + ') == 0'

    # $=
    elif condition['op'] == '$=':
        ret += var + '[' + key + '].rpartition(' + final_value + ")[2] == ''"

    # *=
    elif condition['op'] == '*=':
        ret += final_value + ' in ' + var + '[' + key + ']'

    # ~=
    elif condition['op'] == '~=':
        ret += final_value + ' in ' + var + '[' + key + "].split(';')"

    # =~
    elif condition['op'] == '=~':
        flags = ''

        m = re.match('/(.*)/$', condition['value'])
        if m:
            condition['value'] = m.group(1)

        m = re.match('/(.*)/i$', condition['value'])
        if m:
            condition['value'] = m.group(1)
            flags = ', re.IGNORECASE'

        ret += 're.search(' + condition['value'] + ', ' + var + '[' + key + ']' + flags + ')'

    # unknown operator?
    else:
      print('unknown condition operator: {op} (key: {key}, value: {value})'.format(**condition))
      return None

    if ret == '':
      return None

    return ret;
