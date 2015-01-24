import pgmapcss.db as db
import re
from .compile_eval import compile_eval
from .compile_pseudo_class_condition import compile_pseudo_class_condition

def compile_condition(condition, stat, var="current['tags']"):
    ret = []
    final_value = None
    negate = False
    result = {}

    if 'value_type' in condition and condition['value_type'] == 'eval':
        result = compile_eval(condition['value'], condition, stat)
        final_value = result['code']

    elif 'value' in condition:
        final_value = repr(condition['value'])

    key = repr(condition['key'])

    # !
    if condition['op'][0:2] == '! ':
        negate = True
        condition['op'] = condition['op'][2:]

    # has_tag
    if condition['op'] == 'has_tag':
        ret.append(key + ' in ' + var)

    # =
    elif condition['op'] == '=':
        ret.append(key + ' in ' + var)
        ret.append(var + '[' + key + '] == ' + final_value)

    # !=
    elif condition['op'] == '!=':
        ret.append('(not ' + key + ' in ' + var + ' or ' + var + '[' + key + '] != ' + final_value + ')')

    # < > <= >=
    elif condition['op'] in ('<', '>', '<=', '>='):
        cmp_map = { '<': 'lt', '>': 'gt', '<=': 'le', '>=': 'ge' }
        ret.append(key + ' in ' + var)
        ret.append('eval_' + cmp_map[condition['op']] + '([ ' + var + '[' + key + '], ' + final_value + " ], current) == 'true'")

    # ^=
    elif condition['op'] == '^=':
        ret.append(key + ' in ' + var)
        ret.append(var + '[' + key + '].startswith(' + final_value + ')')

    # $=
    elif condition['op'] == '$=':
        ret.append(key + ' in ' + var)
        ret.append(var + '[' + key + '].endswith(' + final_value + ')')

    # *=
    elif condition['op'] == '*=':
        ret.append(key + ' in ' + var)
        ret.append(final_value + ' in ' + var + '[' + key + ']')

    # ~=
    elif condition['op'] == '~=':
        ret.append(key + ' in ' + var)
        ret.append(final_value + ' in ' + var + '[' + key + "].split(';')")

    # @=
    elif condition['op'] == '@=':
        if condition['value_type'] == 'value':
            ret.append(key + ' in ' + var)
            ret.append(var + '[' + key + '] in ' + repr(set(condition['value'].split(';'))))
        else:
            ret.append(key + ' in ' + var)
            ret.append(var + '[' + key + '] in ' + final_value + '.split(";")')

    # =~
    elif condition['op'] == '=~':
        flags = ''

        if 'i' in condition['regexp_flags']:
            flags = ', re.IGNORECASE'

        ret.append(key + ' in ' + var)
        ret.append('re.search(' + repr('(' + condition['value'] + ')') + ', ' + var + '[' + key + ']' + flags + ')')

    # !~
    elif condition['op'] == '!~':
        flags = ''

        if 'i' in condition['regexp_flags']:
            flags = ', re.IGNORECASE'

        ret.append('(not ' + key + ' in ' + var + ' or not re.search(' + repr('(' + condition['value'] + ')') + ', ' + var + '[' + key + ']' + flags + '))')

    # eval(...)
    elif condition['op'] == 'eval':
        # overwrite result, so that options will be returned
        result = compile_eval(condition['key'], condition, stat)
        ret.append(result['code'] + " not in ('', 'false', 'no', '0', None)")

    elif condition['op'] == 'pseudo_class':
        return compile_pseudo_class_condition(condition, stat)

    elif condition['op'] in ('key_regexp', 'key_regexp_case'):
        flags = ''
        if condition['op'] == 'key_regexp_case':
            flags = ', re.IGNORECASE'

        ret.append('len([ k for k, v in ' + var + '.items() if re.search(' + repr(condition['key']) + ', k' + flags + ') ])')

    # unknown operator?
    else:
      print('unknown condition operator: {op} (key: {key}, value: {value})'.format(**condition))
      return None

    if ret == '':
      return None

    if negate:
        ret = ['not (' + ' and '.join(ret) + ')']

    result['code'] = ret
    return result
