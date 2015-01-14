from .compile_statement import compile_statement
from .compile_selector_part import compile_selector_part
import copy
from collections import Counter

def compile_function_check(statements, min_scale, max_scale, stat, types=None, not_types=set(), function_name_suffix=None):
    replacement = {
      'style_id': stat['id'],
      'min_scale': min_scale,
      'max_scale': max_scale,
      'function_name_suffix': function_name_suffix or str(min_scale).replace('.', '_'),
      'pseudo_elements': repr(stat['pseudo_elements'])
    }

    ret = '''
def check_{function_name_suffix}(object):
# initialize variables
    current = {{
        'object': object,
        'pseudo_elements': {pseudo_elements},
        'tags': object['tags'],
        'types': list(object['types']),
        'properties': {{
            pseudo_element: {{ }}
            for pseudo_element in {pseudo_elements}
         }},
        'has_pseudo_element': {{
            pseudo_element: False
            for pseudo_element in {pseudo_elements}
         }},
    }}

# All statements
'''.format(**replacement)

    compiled_statements = []
    for i in statements:
        if types is not None and not i['selector']['type'] in types:
            continue
        if types is None and i['selector']['type'] in not_types:
            continue

        # create a copy of the statement and modify min/max scale
        i = copy.deepcopy(i)
        i['selector']['min_scale'] = min_scale
        i['selector']['max_scale'] = max_scale

        # if the statement has a parent selector, check if the current object
        # might be a parent. if yes, return with state "pending"
        if 'parent_selector' in i:
            r = {
                'check': compile_selector_part(i['parent_selector'], stat),
                'body': "yield (('pending', " + str(i['id']) + "))\n"
            }
            compiled_statements.append(r)

        compiled_statements.append(compile_statement(i, stat))

    check_count = dict(Counter([
        check
        for c in compiled_statements
        for check in c['check']
    ]))

    def sort_check_count(c):
        return check_count[c]

    indent = '    '
    current_checks = []
    for i in compiled_statements:
        checks = i['check']
        checks.sort(key=sort_check_count, reverse=True)
        combinable = True
        for c in reversed(current_checks):
            if not c in checks:
                if combinable:
                    indent = indent[4:]
                    current_checks = current_checks[:-1]
                else:
                    indent = '    '
                    current_checks = []
                    break
            else:
                combinable = False

        for c in checks:
            if not c in current_checks:
                current_checks += [ c ]
                ret += indent + 'if ' + c + ":\n"
                indent += '    '

        ret += '\n'.join(indent + x for x in i['body'].splitlines())
        ret += "\n"

    ret += '''\
    # iterate over all pseudo-elements, sorted by 'object-z-index' if available
    for pseudo_element in sorted({pseudo_elements}, key=lambda s: to_float(current['properties'][s]['object-z-index'], 0.0) if 'object-z-index' in current['properties'][s] else 0):
        if current['has_pseudo_element'][pseudo_element]:
            current['pseudo_element'] = pseudo_element # for eval functions

            ret = build_result(current, pseudo_element)

            yield(( 'result', ret))
'''.format(**replacement)

    return ret
