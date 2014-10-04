from pkg_resources import *
import pgmapcss.db as db
from .compile_function_get_where import compile_function_get_where
from .compile_function_check import compile_function_check
from ..includes import include_text
import pgmapcss.eval
import pgmapcss.mode
import pgmapcss.types

def compile_function_match(stat):
    scale_denominators = sorted(stat.all_scale_denominators(), reverse=True)

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

    stat['global_data'] = {}
    # get global data from type
    for prop in stat.properties():
        prop_type = pgmapcss.types.get(prop, stat)
        d = prop_type.get_global_data()
        if d:
            stat['global_data'][prop] = d
            stat.clear_property_values_cache()

    replacement = {
      'style_id': stat['id'],
      'host': stat['args'].host,
      'password': stat['args'].password,
      'database': stat['args'].database,
      'user': stat['args'].user,
      'style_element_property': repr({
          k: v['value'].split(';')
          for k, v in stat['defines']['style_element_property'].items()
      }),
      'scale_denominators': repr(scale_denominators),
      'match_where': compile_function_get_where(stat['id'], stat),
      'db_query': db.query_functions(stat),
      'function_check': check_functions,
      'check_chooser': check_chooser,
      'eval_functions': \
resource_string(pgmapcss.eval.__name__, 'base.py').decode('utf-8') +\
pgmapcss.eval.functions().print(indent='') +\
include_text()
    }

    ret = '''\
import pghstore
import re
import math
import datetime
'''.format(**replacement)

    if 'profiler' in stat['options']:
        ret += 'time_start = datetime.datetime.now() # profiling\n'

    ret += '''\
global current
global render_context
current = None

if type(bbox) == list and len(bbox) == 4:
    plan = plpy.prepare('select ST_Transform(SetSRID(MakeBox2D(ST_Point($1, $2), ST_Point($3, $4)), 4326), 900913) as bounds', ['float', 'float', 'float', 'float'])
    res = plpy.execute(plan, [float(b) for b in bbox])
    _bbox = res[0]['bounds']
else:
    _bbox = bbox

render_context = {{ 'bbox': _bbox, 'scale_denominator': scale_denominator }}
'''.format(**replacement)

    if 'context' in stat['options']:
        ret += 'plpy.warning(render_context)\n'

    ret += 'global_data = ' + repr(stat['global_data']) + '\n'

    ret += '''\
{db_query}
{eval_functions}
{function_check}
match_where = None
{match_where}
counter = {{ 'rendered': 0, 'total': 0 }}

{check_chooser}
combined_objects = {{}}
all_style_elements = _all_style_elements
style_element_property = {style_element_property}
for style_element in all_style_elements:
    if not style_element in style_element_property:
        style_element_property[style_element] = []

'''.format(**replacement)

    func = "objects(render_context.get('bbox'), match_where)"
    if 'profiler' in stat['options']:
        ret += "time_qry_start = datetime.datetime.now() # profiling\n"
        ret += "src = list(" + func + ")\n"
        ret += "time_qry_stop = datetime.datetime.now() # profiling\n"
        ret += "plpy.warning('querying db objects took %.2fs' % (time_qry_stop - time_qry_start).total_seconds())\n"
    else:
        ret += "src = " + func + "\n"

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
                plpy.warning('unknown check result: ', result)
            elif result[0] == 'result':
                result = result[1]
                shown = True

                # create a list of all style elements where the current
                # object/pseudo_element is being shown, with a tuple of
                # [ ( style_element, index in style_element list, layer,
                # z-index ), ... ], e.g.:
                # [
                #   ( 'line', 2, 0, 5 ),
                #   ( 'line-text', 5, 103, 5 )
                # ]
                style_elements = [
                    (
                        style_element,
                        i,
                        to_float(result['properties'][style_element + '-layer'] if style_element + '-layer' in result['properties'] else (result['properties']['layer'] if 'layer' in result['properties'] else 0)),
                        to_float(result['properties'][style_element + '-z-index'] if style_element + '-z-index' in result['properties'] else (result['properties']['z-index'] if 'z-index' in result['properties'] else 0))
                    )
                    for i, style_element in enumerate(_all_style_elements)
                    if len({{
                        k
                        for k in style_element_property[style_element]
                        if k in result['properties'] and result['properties'][k]
                    }})
                ]
    '''.format(**replacement)

                # now build the return columns
    if stat['mode'] == 'database-function':
        ret += '''
                yield {{
                    'id': result['id'],
                    'types': result['types'],
                    'tags': pghstore.dumps(result['tags']),
                    'pseudo_element': result['pseudo_element'],
                    'geo': result['geo'],
                    'properties': pghstore.dumps(result['properties']),
                    'style_elements': [ se[0] for se in style_elements ],
                    'style_elements_index': [ se[1] for se in style_elements ],
                    'style_elements_layer': [ se[2] for se in style_elements ],
                    'style_elements_z_index': [ se[3] for se in style_elements ],
                }}
        '''.format(**replacement)

    elif stat['mode'] == 'standalone':
        ret += '''
                yield {{
                    'id': result['id'],
                    'types': result['types'],
                    'tags': result['tags'],
                    'pseudo_element': result['pseudo_element'],
                    'geo': result['geo'],
                    'properties': result['properties'],
                    'style_elements': [ se[0] for se in style_elements ],
                    'style_elements_index': [ se[1] for se in style_elements ],
                    'style_elements_layer': [ se[2] for se in style_elements ],
                    'style_elements_z_index': [ se[3] for se in style_elements ],
                    'object': object,
                }}
        '''.format(**replacement)

    ret += '''
            elif result[0] == 'combine':
                shown = True
                if result[1] not in combined_objects:
                    combined_objects[result[1]] = {{}}
                if result[2] not in combined_objects[result[1]]:
                    combined_objects[result[1]][result[2]] = []
                combined_objects[result[1]][result[2]].append(result[3])
            else:
                plpy.warning('unknown check result: ', result)

        if shown:
            counter['rendered'] += 1
#        else:
#            plpy.warning('not rendered: ' + object['id'] + ' ' + repr(object['tags']))

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
    '''.format(**replacement)

    if 'profiler' in stat['options']:
        ret += '''\
time_stop = datetime.datetime.now() # profiling
plpy.warning('total run of processing (incl. querying db objects) took %.2fs' % (time_stop - time_start).total_seconds())
if counter['total'] == 0:
    counter['perc'] = 100.0
else:
    counter['perc'] = counter['rendered'] / counter['total'] * 100.0
plpy.warning('rendered map features: {{rendered}} / {{total}}, {{perc:.2f}}%'.format(**counter))
'''.format(**replacement);

    if 'rusage' in stat['options']:
        ret += '''\
import resource
plpy.warning('Resource Usage: ' + str(resource.getrusage(resource.RUSAGE_SELF)) + '\\nsee https://docs.python.org/3/library/resource.html')
'''.format(**replacement);

    indent = ''
    if stat['mode'] == 'standalone':
        indent = '    '

    header = resource_string(pgmapcss.mode.__name__, stat['mode'] + '/header.inc')
    header = header.decode('utf-8').format(**replacement)

    footer = resource_string(pgmapcss.mode.__name__, stat['mode'] + '/footer.inc')
    footer = footer.decode('utf-8').format(**replacement)

    ret = header + indent + ret.replace('\n', '\n' + indent) + '\n' + footer

    return ret
