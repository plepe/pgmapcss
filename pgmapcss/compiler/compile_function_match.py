from pkg_resources import *
import pgmapcss.db as db
from .compile_function_get_where import compile_function_get_where
from .compile_function_check import compile_function_check
from ..includes import include_text
import pgmapcss.eval
from .stat import *

def compile_function_match(stat):
    scale_denominators = sorted(stat_all_scale_denominators(stat), reverse=True)

    check_functions = ''
    max_scale = None
    for min_scale in scale_denominators:
        check_functions += compile_function_check([
            v
            for v in stat['statements']
            if v['selector']['min_scale'] <= min_scale and
                (v['selector']['max_scale'] == None or v['selector']['max_scale'] >= (max_scale or 10E+10))
        ], min_scale, max_scale, stat)
        check_functions += '\n'
        max_scale = min_scale

    check_chooser  = "if render_context['scale_denominator'] is None:\n"
    check_chooser += "    check = check_0\n"

    for i in scale_denominators:
        check_chooser += "elif render_context['scale_denominator'] >= %i:\n" % i
        check_chooser += "    check = check_%s\n" % str(i).replace('.', '_')

    replacement = {
      'style_id': stat['id'],
      'style_element_property': repr({
          k: v['value'].split(';')
          for k, v in stat['defines']['style_element_property'].items()
      }),
      'scale_denominators': repr(scale_denominators),
      'match_where': compile_function_get_where(stat['id'], stat),
      'db_query': db.query_functions(),
      'function_check': check_functions,
      'check_chooser': check_chooser,
      'eval_functions': \
resource_string(pgmapcss.eval.__name__, 'base.py').decode('utf-8') +\
pgmapcss.eval.functions().print(indent='') +\
include_text()
    }

    ret = '''\
create or replace function pgmapcss_{style_id}(
  IN bbox                geometry,
  IN scale_denominator   float,
  _all_style_elements\ttext[] default Array['default']
) returns setof pgmapcss_result as $body$
import pghstore
import re
import datetime
'''.format(**replacement)

    if 'profiler' in stat['options']:
        ret += 'time_start = datetime.datetime.now() # profiling\n'

    ret += '''\
global current
global render_context
current = None
render_context = {{ 'bbox': bbox, 'scale_denominator': scale_denominator }}
'''.format(**replacement)

    if 'context' in stat['options']:
        ret += 'plpy.notice(render_context)\n'

    ret += '''\
{db_query}
{eval_functions}
{function_check}
match_where = None
{match_where}
counter = {{ 'rendered': 0, 'total': 0 }}

{check_chooser}
combined_objects = {{}}
results = []
all_style_elements = _all_style_elements
# dirty hack - when render_context.bbox is null, pass type of object instead of style-element
if render_context['bbox'] == None:
    src = [{{
        'types': all_style_elements,
        'tags': {{}},
        'id': '',
        'geo': None
    }}]
    all_style_elements = ['default']
else:
'''.format(**replacement)

    func = "objects(render_context.get('bbox'), match_where)"
    if 'profiler' in stat['options']:
        ret += "    time_qry_start = datetime.datetime.now() # profiling\n"
        ret += "    src = list(" + func + ")\n"
        ret += "    time_qry_stop = datetime.datetime.now() # profiling\n"
        ret += "    plpy.notice('querying db objects took %.2fs' % (time_qry_stop - time_qry_start).total_seconds())\n"
    else:
        ret += "    src = " + func + "\n"

    ret += '''\

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
        shown = False
        counter['total'] += 1
        for result in check(object):
            if type(result) != tuple or len(result) == 0:
                plpy.notice('unknown check result: ', result)
            elif result[0] == 'result':
                shown = True
                results.append(result[1])
            elif result[0] == 'combine':
                shown = True
                if result[1] not in combined_objects:
                    combined_objects[result[1]] = {{}}
                if result[2] not in combined_objects[result[1]]:
                    combined_objects[result[1]][result[2]] = []
                combined_objects[result[1]][result[2]].append(result[3])
            else:
                plpy.notice('unknown check result: ', result)

        if shown:
            counter['rendered'] += 1
#        else:
#            plpy.notice('not rendered: ' + object['id'] + ' ' + repr(object['tags']))

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

layers = sorted(
    set(
        x['properties'].get('layer', 0)
        for x in results
    ).union(set(
        x['properties'].get(style_element + '-layer')
        for x in results
        for style_element in all_style_elements
        if style_element + '-layer' in x['properties']
    )),
    key=lambda x: to_float(x, 0)
)
if None in layers:
    layers.remove(None)

for layer in layers:
    for style_element in all_style_elements:
        result_list = []

        for result in results:
            result_layer = result['properties'].get(style_element + '-layer') or result['properties'].get('layer') or '0'
            if result_layer == layer:
                # check if any property for the current style element is set (or
                # there is no entry for the current style element in
                # @style_element_property
                if {style_element_property}.get(style_element) == None or \
                    len(set(
                    True
                    for k in {style_element_property}.get(style_element)
                    if result['properties'].get(k)
                )):
                    result_list.append(result)

        result_list = sorted(result_list,
            key=lambda x: to_float(
                x['properties'].get(style_element + '-z-index') or
                x['properties'].get('z-index')
                , 0))

        for result in result_list:
            x = {{
                'id': result['id'],
                'types': result['types'],
                'tags': pghstore.dumps(result['tags']),
                'style-element': style_element,
                'pseudo_element': result['pseudo_element'],
                'geo': result['geo'],
                'properties': pghstore.dumps(result['properties'])
            }}
            yield x

'''.format(**replacement)

    if 'profiler' in stat['options']:
        ret += '''\
time_stop = datetime.datetime.now() # profiling
plpy.notice('total run of processing (incl. querying db objects) took %.2fs' % (time_stop - time_start).total_seconds())
if counter['total'] == 0:
    counter['perc'] = 100.0
else:
    counter['perc'] = counter['rendered'] / counter['total'] * 100.0
plpy.notice('rendered map features: {{rendered}} / {{total}}, {{perc:.2f}}%'.format(**counter))
'''.format(**replacement);

    ret += '''\
$body$ language 'plpython3u' immutable;
'''.format(**replacement);

    return ret
