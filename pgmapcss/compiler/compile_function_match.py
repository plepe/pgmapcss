import pgmapcss.db as db
from .compile_function_get_where import compile_function_get_where
from .compile_function_check import compile_function_check
from pkg_resources import *
import pgmapcss.eval
import pgmapcss.colors

def compile_function_match(stat):
    replacement = {
      'style_id': stat['id'],
      'style_element_property': repr({
          k: v['value'].split(';')
          for k, v in stat['defines']['style_element_property'].items()
      }),
      'match_where': compile_function_get_where(stat['id'], stat),
      'db_query': db.query_functions(),
      'function_check': compile_function_check(stat['id'], stat),
      'eval_functions': '''\
# eval-functions
def to_float(v, default=None):
    try:
        return float(v)
    except ValueError:
        return default
def to_int(v, default=None):
    try:
        return int(v)
    except ValueError:
        return default
def debug(text):
    plpy.notice(text)
def float_to_str(v, default=None):
    r = repr(v)
    if r[-2:] == '.0':
        r = r[:-2]
    return r
''' +\
pgmapcss.eval.functions().print(indent='') +\
resource_string(pgmapcss.colors.__name__, 'to_color.py').decode('utf-8') +\
resource_string(pgmapcss.colors.__name__, 'color_values.py').decode('utf-8')
    }

    ret = '''\
create or replace function {style_id}_match(
  IN bbox                geometry,
  IN scale_denominator   float,
  _all_style_elements\ttext[] default Array['default']
) returns setof pgmapcss_result as $body$
import pghstore
import re
import datetime
time_start = datetime.datetime.now() # profiling
global current
global render_context
current = None
render_context = {{ 'bbox': bbox, 'scale_denominator': scale_denominator }}
{db_query}
{eval_functions}
{function_check}
match_where = None
{match_where}

combined_objects = {{}}
results = []
all_style_elements = _all_style_elements
# dirty hack - when render_context.bbox is null, pass type of object instead of style-element
if render_context['bbox'] == None:
    src = [{{
        'types': all_style_elements,
        'tags': {{}},
        'id': '',
        'geo': ''
    }}]
    all_style_elements = ['default']
else:
    src = objects(render_context.get('bbox'), match_where)

def ST_Collect(geometries):
    plan = plpy.prepare('select ST_Collect($1) as r', ['geometry[]'])
    res = plpy.execute(plan, [geometries])
    return res[0]['r']

def dict_merge(dicts):
    ret = {{}}

    for d in dicts:
        for k, v in d.items():
            if k not in ret:
                ret[k] = set()

            ret[k].add(v)

    for k, vs in ret.items():
        ret[k] = ';'.join(vs)

    return ret

while src:
    for object in src:
        for result in check(object):
            if type(result) != tuple or len(result) == 0:
                plpy.notice('unknown check result: ', result)
            elif result[0] == 'result':
                results.append(result[1])
            elif result[0] == 'combine':
                if result[1] not in combined_objects:
                    combined_objects[result[1]] = {{}}
                if result[2] not in combined_objects[result[1]]:
                    combined_objects[result[1]][result[2]] = []
                combined_objects[result[1]][result[2]].append(result[3])
            else:
                plpy.notice('unknown check result: ', result)

    src = None

    if len(combined_objects):
        src = []
        for combine_type, items in combined_objects.items():
            for combine_id, obs in items.items():
                src.append({{
                    'id': ';'.join([ ob['id'] for ob in obs ]),
                    'types': [ combine_type ],
                    'tags': dict_merge([ ob['tags'] for ob in obs ]),
                    'geo': ST_Collect([ ob['geo'] for ob in obs ])
                }})

        combined_objects = []

layers = sorted(set(
    x['properties'].get('layer', 0)
    for x in results
), key=lambda x: to_float(x, 0))

for layer in layers:
    results_layer = sorted([
        x
        for x in results
        if x['properties'].get('layer', 0) == layer
    ],
    key=lambda x: to_float(x['properties'].get('z-index'), 0))

    for style_element in all_style_elements:
        for result in results_layer:
            # check if any property for the current style element is set (or
            # there is no entry for the current style element in
            # @style_element_property
            if {style_element_property}.get(style_element) == None or \
                len(set(
                True
                for k in {style_element_property}.get(style_element)
                if result['properties'].get(k)
            )):
                yield {{
                    'id': result['id'],
                    'types': result['types'],
                    'tags': pghstore.dumps(result['tags']),
                    'style-element': style_element,
                    'pseudo_element': result['pseudo_element'],
                    'geo': result['geo'],
                    'properties': pghstore.dumps(result['properties'])
                }}

time_stop = datetime.datetime.now() # profiling
plpy.notice('total run of match() (incl. querying db objects) took %.2fs' % (time_stop - time_start).total_seconds())

$body$ language 'plpython3u' immutable;
'''.format(**replacement);

    return ret
