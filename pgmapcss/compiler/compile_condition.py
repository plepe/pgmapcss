import pgmapcss.db as db
import re
from .compile_eval import compile_eval

def compile_condition(condition, stat, prefix='current.', match_where=False):
    ret = ''

    if condition['value_type'] == 'eval':
        final_value = compile_eval(condition['value'])

    else:
        final_value = db.format(condition['value'])

    # when compiling for get_where()
    if match_where:
        # ignore generated tags (identified by leading .)
        if condition['key'][0] == '.':
            return None

        # eval() statements
        if condition['value_type'] == 'eval':
          # ignore 'not' statements
          if condition['op'][0:2] == '! ':
            return None

          # treat other conditions as has_key
          else:
            return prefix + 'tags ? ' + db.format(condition['key']);

    # !
    if condition['op'][0:2] == '! ':
        print('here')
        ret += 'not '
        condition['op'] = condition['op'][2:]

    # has_tag
    if condition['op'] == 'has_tag':
        ret += prefix + 'tags ? ' + db.format(condition['key'])

    # =
    elif condition['op'] == '=':
        if condition['value_type'] == None:
            ret += prefix + 'tags @> ' + db.format({ condition['key']: condition['value'] })
        else:
            ret += prefix + 'tags->' + db.format(condition['key']) + ' = ' + final_value

    # !=
    elif condition['op'] == '!=':
        if condition['value_type'] == None:
            ret += 'not ' + prefix + 'tags @> ' + db.format({ condition['key']: condition['value'] })
        else:
            ret += prefix + 'tags->' + db.format(condition['key']) + ' != ' + final_value

    # < > <= >=
    elif condition['op'] in ('<', '>', '<=', '>='):
        if condition['value_type'] == None:
            ret += 'pgmapcss_to_float(' + prefix + 'tags->' + db.format(condition['key']) + ') ' + condition['op'] + ' ' + final_value;
        else:
            ret += 'pgmapcss_to_float(' + prefix + 'tags->' + db.format(condition['key']) + ') ' + condition['op'] + ' pgmapcss_to_float(' + final_value + ')';

    # ^=
    elif condition['op'] == '^=':
        ret += prefix + 'tags->' + db.format(condition['key']) + ' similar to (' + final_value + ' || \'%\')';

    # $=
    elif condition['op'] == '$=':
        ret += prefix + 'tags->' + db.format(condition['key']) + ' similar to (\'%\' || ' + final_value + ')';

    # *=
    elif condition['op'] == '*=':
        ret += prefix + 'tags->' + db.format(condition['key']) + ' similar to (\'%\' || ' + final_value + ' || \'%\')';

    # ~=
    elif condition['op'] == '~=':
        ret += final_value + ' = any(string_to_array(' + prefix + 'tags->' + db.format(condition['key']) + ', \';\'))';

    # =~
    elif condition['op'] == '=~':
        condition['op'] = '~';

        m = re.match('/(.*)/$', condition['value'])
        if m:
            condition['value'] = m.group(1)
            condition['op'] = '~'

        m = re.match('/(.*)/i$', condition['value'])
        if m:
            condition['value'] = m.group(1)
            condition['op'] = '~*'

        ret += prefix + 'tags->' + db.format(condition['key']) + ' ' + condition['op'] + ' ' + db.format(condition['value'])

    # unknown operator?
    else:
      print('unknown condition operator: {op} (key: {key}, value: {value})'.format(**condition))
      return None

    if ret == '':
      return None

    return ret;
