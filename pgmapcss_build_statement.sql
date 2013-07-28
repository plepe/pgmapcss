create or replace function pgmapcss_build_statement (
  selectors pgmapcss_selector_return[],
  properties pgmapcss_properties_return,
  pgmapcss_compile_stat
)
returns pgmapcss_compile_stat
as $$
#variable_conflict use_variable
declare
  stat pgmapcss_compile_stat;
  ret text := ''::text;
  a text[];
  r pgmapcss_selector_return;
begin
  stat := $3;
  ret = ret || 'if   (';

  a = Array[]::text[];
  foreach r in array selectors loop
    a = array_append(a, array_to_string(r.conditions, ' and '));
  end loop;
  ret = ret || array_to_string(a, E')\n  or (');

  ret = ret || E')\nthen\n';
  ret = ret || '  style = style || ' || quote_nullable(cast(properties.properties as text)) || E';\n';

  ret = ret || E'end if;\n\n';

  stat.func = stat.func || ret;

  return stat;
end;
$$ language 'plpgsql' immutable;
