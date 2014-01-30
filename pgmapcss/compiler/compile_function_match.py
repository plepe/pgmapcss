import pgmapcss.db as db
from .compile_function_get_where import compile_function_get_where
from .compile_function_check import compile_function_check
from pkg_resources import *

def compile_function_match(id, stat):
    replacement = {
      'style_id': id,
      'style_element_property': repr({
          k: v['value'].split(';')
          for k, v in stat['defines']['style_element_property'].items()
      }),
      'match_where': compile_function_get_where(id, stat),
      'db_query': db.query_functions(),
      'function_check': compile_function_check(id, stat)
    }

    ret = '''\
create or replace function {style_id}_match(
  render_context\tpgmapcss_render_context,
  all_style_elements\ttext[] default Array['default']
) returns setof pgmapcss_result as $body$
import pghstore
import re
#  t timestamp with time zone; -- profiling
#  t := clock_timestamp(); -- profiling
{db_query}
{function_check}
match_where = None
{match_where}

results = []
for object in objects(match_where):
    for result in check(object):
        if type(result) != tuple or len(result) == 0:
            plpy.notice('unknown check result: ', result)
        elif result[0] == 'result':
            results.append(result[1])
        elif result[0] == 'combine':
            pass
        else:
            plpy.notice('unknown check result: ', result)

layers = sorted(set(
    x['properties'].get('layer', 0)
    for x in results
), key=float)

for layer in layers:
    results_layer = sorted([
        x
        for x in results
        if x['properties'].get('layer', 0) == layer
    ],
    key=lambda x: x['properties'].get('z-index', 0))

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

$body$ language 'plpython3u' immutable;
'''.format(**replacement);

    ret1 = '''\
create or replace function {style_id}_match(
  render_context\tpgmapcss_render_context,
  "all-style-elements"\ttext[] default Array['default']
) returns setof pgmapcss_result as $body$
declare
  ret pgmapcss_result;
  "max-style-element" int;
begin
  "max-style-element" := array_upper("all-style-elements", 1);
  return query
    select * from (
    select
      id, tags, geo, types, pseudo_element, properties,
      unnest("all-style-elements") as "style-element", null::text, null::text
    from
      (select (result).* from
        (select
          (CASE WHEN (result).combine_type is null THEN (array_agg(result))[1]
          ELSE {style_id}_check(
            pgmapcss_object(string_agg((result).id, ';'), hstore_merge(array_agg((result).tags)), ST_Collect((result).geo), Array[(result).combine_type]), render_context)
          END) result from
        (select
          {style_id}_check(
            object, render_context
          ) result
        from
          objects(render_context, {style_id}_get_where(render_context)) object
        offset 0) t
        group by (result).combine_type, coalesce((result).combine_id, (result).id || (result).pseudo_element) offset 0) t) t
        order by
          pgmapcss_to_float(properties->'layer') asc,
          generate_series(1, "max-style-element") asc,
          coalesce(cast(properties->'z-index' as float), 0) asc
        ) t where
          (select true = any(array_agg(x is not null)) from (select unnest(properties->(cast({style_element_property}->("style-element") as text[]))) x) t1) or not {style_element_property} ? ("style-element");
    raise notice 'total run of match() (incl. querying db objects) took %', clock_timestamp() - t; -- profiling
    return;
end;
$body$ language 'plpgsql' immutable;
'''.format(**replacement);

    return ret
