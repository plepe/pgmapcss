from .compile_statement import compile_statement
from .compile_eval import compile_eval
from .stat import *
import pgmapcss.db as db

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
      'pseudo_elements': db.format(stat['pseudo_elements']),
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

    # handle @values, @default_other for all properties
    done_prop = []
    # start with props from @depend_property
    for main_prop, props in stat['defines']['depend_property'].items():
        props = props['value'].split(';')
        r = ''

        r += print_checks(main_prop, stat)
        done_prop.append(main_prop)

        for prop in props:
            r += print_checks(prop, stat, main_prop=main_prop)
            done_prop.append(prop)

        if r != '':
            ret += '      if current.styles[r.i] ? ' + db.format(main_prop) + ' then\n'
            ret += r
            ret += '      end if;\n'

    for prop in [ prop for prop in stat_properties(stat) if not prop in done_prop ]:
        ret += print_checks(prop, stat)

    # postprocess requested properties (see @postprocess)
    for k, v in stat['defines']['postprocess'].items():
        ret += '      current.styles[r.i] := current.styles[r.i] || hstore(' + db.format(k) + ', ' + compile_eval(v['value']) + ');\n'

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
