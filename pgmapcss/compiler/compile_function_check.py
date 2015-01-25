from .compile_statement import compile_statement
from .compile_selector_part import compile_selector_part
import copy
from collections import Counter
from .compile_requirements import compile_requirements

def compile_function_check(statements, min_scale, max_scale, stat):
    replacement = {
      'style_id': stat['id'],
      'min_scale': min_scale,
      'max_scale': max_scale,
      'min_scale_esc': str(min_scale).replace('.', '_'),
      'pseudo_elements': repr(stat['pseudo_elements'])
    }

    ret = '''
def check_{min_scale_esc}(object):
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
        # create a copy of the statement and modify min/max scale
        i = copy.deepcopy(i)
        i['selector']['min_scale'] = min_scale
        i['selector']['max_scale'] = max_scale

        # if the statement has a parent selector, check if the current object
        # might be a parent. if yes, return with state "pending"
        if 'parent_selector' in i:
            result = compile_selector_part(i['parent_selector'], stat)
            result['body'] = "yield ('pending', " + str(i['id']) + ")\n"
            result['check'] = result['code']
            del result['code']
            print('parent_selector', result)
            compiled_statements.append(result)

        compiled_statements.append(compile_statement(i, stat))

    check_count = dict(Counter([
        check['code']
        for c in compiled_statements
        for check in c['check']
    ]))

    def sort_check_count(c):
        return check_count[c['code']]

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
                if 'options' in c:
                    ret += compile_requirements(c['options'], { 'id': i['id'] }, stat, indent=indent)
                ret += indent + 'if ' + c['code'] + ":\n"
                indent += '    '

        ret += '\n'.join(indent + x for x in i['body'].splitlines())
        ret += "\n"

    ret += '''\
    # iterate over all pseudo-elements, sorted by 'object-z-index' if available
    for pseudo_element in sorted({pseudo_elements}, key=lambda s: to_float(current['properties'][s]['object-z-index'], 0.0) if 'object-z-index' in current['properties'][s] else 0):
        if current['has_pseudo_element'][pseudo_element]:
            current['pseudo_element'] = pseudo_element # for eval functions

            ret = build_result(current, pseudo_element)

            # if 'geo' has been modified, it can be read from properties, if
            # not directly from object
            if 'geo' in current['properties'][pseudo_element]:
                # set geo as return value AND remove key from properties
                ret['geo'] = current['properties'][pseudo_element].pop('geo');
            else:
                if not 'geo' in current['object']:
                    yield 'request', 999999999999999, {{ 'type': 'objects_by_id', 'options': {{ 'requirements': {{'geo'}} }} }}
                ret['geo'] = current['object']['geo']

            yield(( 'result', ret))
'''.format(**replacement)

    return ret
