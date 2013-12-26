from .compile_statement import compile_statement

def compile_function(id, stat):
    replacement = {
      'style_id': id
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
'''.format(**replacement)

    stat['properties_values'] = {}

    for i in stat['statements']:
        ret += compile_statement(i, stat)

    ret += '''\
  return;
end;
$body$ language 'plpgsql' immutable;
'''.format(**replacement)

    return ret
