from .compile_statement import compile_statement
from .compile_eval import compile_eval
from .stat import *
import copy
import textwrap
from collections import Counter

def print_postprocess(prop, stat, indent=''):
    ret = ''

    # postprocess requested properties (see @postprocess)
    if prop in stat['defines']['postprocess']:
        v = stat['defines']['postprocess'][prop]
        ret += indent + "current['properties'][pseudo_element][" + repr(prop) +\
           "] = " + compile_eval(v['value'], v, stat) + '\n'

    return ret

def print_checks(prop, stat, main_prop=None, indent=''):
    ret = ''

    # @default_other
    if 'default_other' in stat['defines'] and prop in stat['defines']['default_other']:
        other = stat['defines']['default_other'][prop]['value']
        ret += indent + 'if not ' + repr(prop) + " in current['properties'][pseudo_element] or current['properties'][pseudo_element][" + repr(prop) + "] is None:\n"
        ret += indent + "    current['properties'][pseudo_element][" + repr(prop) + "] = current['properties'][pseudo_element][" + repr(other) + "] if " + repr(other) + " in current['properties'][pseudo_element] else None\n"

    # @default_value
    if 'default_value' in stat['defines'] and prop in stat['defines']['default_value'] and stat['defines']['default_value'][prop]['value'] is not None:
        ret += indent + 'if ' + repr(prop) + " not in current['properties'][pseudo_element]:\n" # or current['properties'][pseudo_element][" + repr(prop) + "] in (None, ''):\n"
        ret += indent + "    current['properties'][pseudo_element][" + repr(prop) + "] = " + repr(stat['defines']['default_value'][prop]['value']) + "\n"

    # @values
    if 'values' in stat['defines'] and prop in stat['defines']['values']:
        values = stat['defines']['values'][prop]['value'].split(';')
        used_values = stat_property_values(prop, stat, include_illegal_values=True)

        # if there are used values which are not allowed, always check
        # resulting value and - if not allowed - replace by the first
        # allowed value
        if len([ v for v in used_values if not v in values ]):
            ret += indent + 'if ' + repr(prop) + " not in current['properties'][pseudo_element] or current['properties'][pseudo_element][" + repr(prop) + "] not in " + repr(values) + ":\n"
            ret += indent + "    current['properties'][pseudo_element][" + repr(prop) + "] = " + repr(values[0]) + '\n'

    return ret

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
    global current
    current = {{
        'object': object,
        'pseudo_elements': {pseudo_elements},
        'tags': object['tags'],
        'types': object['types'],
        'properties': {{
            pseudo_element: {{ 'geo': object['geo'] }}
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

        ret += textwrap.indent(i['body'], indent)
        ret += "\n"

    ret += '''\
    # iterate over all pseudo-elements, sorted by 'object-z-index' if available
    for pseudo_element in sorted({pseudo_elements}, key=lambda s: to_float(current['properties'][s]['object-z-index'], 0.0) if 'object-z-index' in current['properties'][s] else 0):
        if current['has_pseudo_element'][pseudo_element]:
            current['pseudo_element'] = pseudo_element # for eval functions

            # Finally build return value(s)
            ret = {{
                'id': object['id'],
                'types': object['types'],
                'tags': current['tags'],
                'pseudo_element': pseudo_element
            }}

'''.format(**replacement)

    # handle @values, @default_other for all properties
    done_prop = []
    indent = '            '

    # make sure, that depend_properties are compiled in the same order as
    # specified in the mapcss file
    main_prop_order = [
        k
        for k, d in stat['defines']['depend_property'].items()
    ]
    def main_prop_order_key(k):
        return stat['defines']['depend_property'][k]['pos']
    main_prop_order.sort(key=main_prop_order_key)

    # start with props from @depend_property
    for main_prop in main_prop_order:
        props = stat['defines']['depend_property'][main_prop]
        include_main_prop = False
        if main_prop in stat_properties(stat):
            include_main_prop = True

        props = props['value'].split(';')
        r = ''

        # main_prop never been used -> skip
        if include_main_prop:
            r += print_checks(main_prop, stat, indent=indent + '    ')
            r += print_postprocess(main_prop, stat, indent=indent + '    ')

        done_prop.append(main_prop)

        for prop in props:
            if include_main_prop:
                r += print_checks(prop, stat, main_prop=main_prop, indent=indent + '    ')

            done_prop.append(prop)

        # finally, post process values
        if include_main_prop:
            for prop in props:
                r += print_postprocess(prop, stat, indent=indent + '    ')
            r += print_postprocess(main_prop, stat, indent=indent + '    ')

        if include_main_prop and r != '':
            ret += indent + 'if ' + repr(main_prop) + " in current['properties'][pseudo_element]:\n"
            ret += r

    for prop in [ prop for prop in stat_properties(stat) if not prop in done_prop ]:
        ret += print_checks(prop, stat, indent=indent)
        ret += print_postprocess(prop, stat, indent=indent)

    ret += '''\
            # set geo as return value AND remove key from properties
            ret['geo'] = current['properties'][pseudo_element].pop('geo');
            ret['properties'] = current['properties'][pseudo_element]
            yield(( 'result', ret))
'''.format(**replacement)

    return ret
