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
  r1 record;
  current_layer text;
begin
  stat := $3;

  foreach r in array selectors loop
    ret = ret || 'if   (';
    if array_upper(r.conditions, 1) is null then
      ret = ret || 'true';
    else
      ret = ret || array_to_string(r.conditions, ' and ');
    end if;
    ret = ret || E')\nthen\n';

    current_layer = array_search(r.layer, stat.layers);
    if current_layer is null then
      stat.layers = array_append(stat.layers, r.layer);
      current_layer = array_upper(stat.layers, 1);
    end if;

    ret = ret || '  current_style = styles[' || current_layer || E'];\n';
    ret = ret || '  styles[' || current_layer || '] = ' ||
      'styles[' || current_layer || '] || ' ||
      quote_nullable(cast(properties.properties as text)) || E';\n';
    ret = ret || '  has_layer[' || current_layer || E'] = true;\n';

    if array_upper(akeys(properties.assignments), 1) is not null then
      ret = ret || '  tags = tags || ' ||
	quote_nullable(cast(properties.assignments as text)) || E';\n';
    end if;

    for r1 in select * from each(properties.eval_assignments) loop
      ret = ret || '  tags = tags || hstore(' ||
        quote_literal(r1.key) || ', ' || r1.value || E');\n';
    end loop;

    for r1 in select * from each(properties.eval_properties) loop
      ret = ret || '  styles[' || current_layer || '] = ' ||
	'styles[' || current_layer || '] || hstore(' ||
        quote_literal(r1.key) || ', ' || r1.value || E');\n';
    end loop;

    if array_upper(properties.unassignments, 1) is not null then
      ret = ret || '  tags = tags - cast(' ||
	quote_nullable(cast(properties.unassignments as text)) || E' as text[]);\n';
    end if;

    ret = ret || E'end if;\n\n';
  end loop;

  stat.func = stat.func || ret;

  return stat;
end;
$$ language 'plpgsql' immutable;
