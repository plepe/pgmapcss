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
  r pgmapcss_selector_return;
  current_layer text;
begin
  stat := $3;

  foreach r in array selectors loop
    ret = ret || 'if   (';
    ret = ret || array_to_string(r.conditions, ' and ');
    ret = ret || E')\nthen\n';

    current_layer = array_search(r.layer, stat.layers);
    if current_layer is null then
      stat.layers = array_append(stat.layers, r.layer);
      current_layer = array_upper(stat.layers, 1);
    end if;

    ret = ret || '  styles[' || current_layer || '] = ' ||
      'styles[' || current_layer || '] || ' ||
      quote_nullable(cast(properties.properties as text)) || E';\n';
    ret = ret || '  has_layer[' || current_layer || E'] = true;\n';

    ret = ret || E'end if;\n\n';
  end loop;

  stat.func = stat.func || ret;

  return stat;
end;
$$ language 'plpgsql' immutable;
