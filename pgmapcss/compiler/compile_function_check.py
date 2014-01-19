from .compile_statement import compile_statement
from .compile_eval import compile_eval
from .stat import *
import pgmapcss.eval

def print_checks(prop, stat, main_prop=None, indent=''):
    ret = ''

    # @default_other
    if 'default_other' in stat['defines'] and prop in stat['defines']['default_other']:
        other = stat['defines']['default_other'][prop]['value']
        ret += indent + 'if not ' + repr(prop) + " in current['properties'][pseudo_element] or current['properties'][pseudo_element][" + repr(prop) + "] is None:\n"
        ret += indent + "    current['properties'][pseudo_element][" + repr(prop) + "] = current['properties'][pseudo_element][" + repr(other) + "] if " + repr(other) + " in current['properties'][pseudo_element] else None\n"

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

def compile_function_check(id, stat):
    replacement = {
      'style_id': id,
      'pseudo_elements': repr(stat['pseudo_elements'])
    }

    ret = '''\
create or replace function {style_id}_check(
  object\tpgmapcss_object,
  render_context\tpgmapcss_render_context
) returns setof pgmapcss_result as $body$
import pghstore
import re
# eval-functions
def to_float(v, default=None):
    try:
        return float(v)
    except ValueError:
        return default
'''.format(**replacement)

    ret += pgmapcss.eval.load().print()

    ret += '''\
# initialize variables
current = {{
    'object': object,
    'pseudo_elements': {pseudo_elements},
    'tags': pghstore.loads(object['tags']),
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

    for i in stat['statements']:
        ret += compile_statement(i, stat)

    ret += '''\
# Finally build return value(s)
ret = {{
    'id': object['id'],
    'types': object['types'],
    'tags': pghstore.dumps(current['tags']),
    'style-element': None,
    'combine_type': None,
    'combine_id': None,
}}

# iterate over all pseudo-elements, sorted by 'object-z-index' if available
for pseudo_element in sorted({pseudo_elements}, key=lambda s: to_float(current['properties'][s]['object-z-index'], 0.0) if 'object-z-index' in current['properties'][s] else 0):
    if current['has_pseudo_element'][pseudo_element]:
        current['pseudo_element'] = pseudo_element # for eval functions
        ret['pseudo_element'] = pseudo_element
'''.format(**replacement)

    # handle @values, @default_other for all properties
    done_prop = []
    indent = '        '
    # start with props from @depend_property
    for main_prop, props in stat['defines']['depend_property'].items():
        props = props['value'].split(';')
        r = ''

        r += print_checks(main_prop, stat, indent=indent + '    ')
        done_prop.append(main_prop)

        for prop in props:
            r += print_checks(prop, stat, main_prop=main_prop, indent=indent + '    ')
            done_prop.append(prop)

        if r != '':
            ret += indent + 'if ' + repr(main_prop) + " in current['properties'][pseudo_element]:\n"
            ret += r

    for prop in [ prop for prop in stat_properties(stat) if not prop in done_prop ]:
        ret += print_checks(prop, stat, indent)

    # postprocess requested properties (see @postprocess)
    for k, v in stat['defines']['postprocess'].items():
        ret += indent + "current['properties'][pseudo_element][" + repr(k) +\
               "] = " + compile_eval(v['value']) + '\n'

    ret += '''\
        # set geo as return value AND remove key from properties
        ret['geo'] = current['properties'][pseudo_element].pop('geo');
        ret['properties'] = pghstore.dumps(current['properties'][pseudo_element])
        yield(ret)

$body$ language 'plpython3u' immutable;
'''.format(**replacement)

    return ret
