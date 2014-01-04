from .compile_statement import compile_statement
from .compile_eval import compile_eval
import pg

def compile_function(id, stat):
    replacement = {
      'style_id': id,
      'pseudo_elements': pg.format(stat['pseudo_elements']),
      'count_pseudo_elements': len(stat['pseudo_elements'])
    }

    ret = '''\
create or replace function {style_id}_check(
  object\tpgmapcss_object,
  render_context\tpgmapcss_render_context
) returns setof pgmapcss_result as $body$
declare
  current pgmapcss_current;
  ret pgmapcss_result;
  r record;
  parent_object record;
  parent_index int;
  o pgmapcss_object;
  i int;
begin
  current.pseudo_elements := {pseudo_elements};
  current.tags := object.tags || hstore('osm_id', object.id);
  current.types := object.types;
  -- initialize all styles with the 'geo' property
  current.styles := array_fill(hstore('geo', object.geo), Array[{count_pseudo_elements}]);
  current.has_pseudo_element := array_fill(false, Array[{count_pseudo_elements}]);

'''.format(**replacement)

    stat['properties_values'] = {}

    for i in stat['statements']:
        ret += compile_statement(i, stat)

    ret += '''
  ret.id=object.id;
  ret.types=object.types;
  ret.tags=current.tags;
  for r in select * from (select generate_series(1, {count_pseudo_elements}) i, unnest(current.styles) style) t order by coalesce(cast(style->'object-z-index' as float), 0) asc loop
    if current.has_pseudo_element[r.i] then
      current.pseudo_element_ind = r.i;
'''.format(**replacement)

    # postprocess requested properties (see @postprocess)
    for k, v in stat['defines']['postprocess'].items():
        ret += '      current.styles[r.i] := current.styles[r.i] || hstore(' + pg.format(k) + ', ' + compile_eval(v['value']) + ');\n'

    ret += '''
      ret.geo=current.styles[r.i]->'geo';
      current.styles[r.i] := current.styles[r.i] - 'geo'::text;
      ret.properties=current.styles[r.i];
      ret.pseudo_element=(current.pseudo_elements)[r.i];
      return next ret;
    end if;
  end loop;

  return;
end;
$body$ language 'plpgsql' immutable;
'''.format(**replacement)

    return ret
