from .compile_statement import compile_statement
from .compile_eval import compile_eval
from .stat import *
import pgmapcss.db as db
import pgmapcss.eval

def print_checks(prop, stat, main_prop=None):
    ret = ''

    # @default_other
    if 'default_other' in stat['defines'] and prop in stat['defines']['default_other']:
        other = stat['defines']['default_other'][prop]['value']
        ret += 'if (current.styles[r.i]->' + db.format(prop) + ') is null ' +\
            'then current.styles[r.i] := current.styles[r.i] || hstore(' +\
            db.format(prop) + ', current.styles[r.i]->' +\
            db.format(other) + '); end if;\n'

    # @values
    if 'values' in stat['defines'] and prop in stat['defines']['values']:
        values = stat['defines']['values'][prop]['value'].split(';')
        used_values = stat_property_values(prop, stat, include_illegal_values=True)

        # if there are used values which are not allowed, always check
        # resulting value and - if not allowed - replace by the first
        # allowed value
        if len([ v for v in used_values if not v in values ]):
            ret += 'if not (current.styles[r.i]->' +\
                db.format(prop) + ') = any(' +\
                db.format(values) + ') then ' +\
                'current.styles[r.i] := current.styles[r.i] || hstore(' +\
                db.format(prop) + ', ' +\
                db.format(values[0]) + '); end if;\n';

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
# eval-functions
def to_float(v):
    try:
        return float(v)
    except ValueError:
        return None
'''.format(**replacement)

    ret += pgmapcss.eval.load().print()

    ret += '''\
# initialize variables
current = {{
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

for pseudo_element in {pseudo_elements}:
    if current['has_pseudo_element'][pseudo_element]:
        ret['pseudo_element'] = pseudo_element
        # set geo as return value AND remove key from properties
        ret['geo'] = current['properties'][pseudo_element].pop('geo');
        ret['properties'] = pghstore.dumps(current['properties'][pseudo_element])
        yield(ret)

$body$ language 'plpython3u' immutable;
'''.format(**replacement)

    return ret
