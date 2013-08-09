create or replace function pgmapcss_build_statement (
  selector pgmapcss_selector,
  properties pgmapcss_rule_properties,
  pgmapcss_compile_stat
)
returns pgmapcss_compile_stat
as $$
#variable_conflict use_variable
declare
  stat pgmapcss_compile_stat;
  ret text := ''::text;
  r pgmapcss_selector_part;
  r1 record;
  current_pseudo_element text;
begin
  stat := $3;

    r := selector.object;

    ret = ret || 'if   (';
    ret = ret || pgmapcss_compile_selector_part(selector.object);
    ret = ret || E')\nthen\n';

    current_pseudo_element = array_search(r.pseudo_element, stat.pseudo_elements);
    if current_pseudo_element is null then
      stat.pseudo_elements = array_append(stat.pseudo_elements, r.pseudo_element);
      current_pseudo_element = array_upper(stat.pseudo_elements, 1);
    end if;

    ret = ret || '  current.pseudo_element = pseudo_elements[' || current_pseudo_element || E'];\n';
    ret = ret || '  current.pseudo_element_ind = ' || current_pseudo_element || E';\n';
    ret = ret || '  current.styles[' || current_pseudo_element || '] = ' ||
      'current.styles[' || current_pseudo_element || '] || ' ||
      quote_nullable(cast(properties.properties as text)) || E';\n';
    ret = ret || '  current.has_pseudo_element[' || current_pseudo_element || E'] = true;\n';

    if array_upper(akeys(properties.assignments), 1) is not null then
      ret = ret || '  current.tags = current.tags || ' ||
	quote_nullable(cast(properties.assignments as text)) || E';\n';
    end if;

    for r1 in select * from each(properties.eval_assignments) loop
      ret = ret || '  current.tags = current.tags || hstore(' ||
        quote_literal(r1.key) || ', ' || r1.value || E');\n';
    end loop;

    for r1 in select * from each(properties.eval_properties) loop
      ret = ret || '  current.styles[' || current_pseudo_element || '] = ' ||
	'current.styles[' || current_pseudo_element || '] || hstore(' ||
        quote_literal(r1.key) || ', ' || r1.value || E');\n';
    end loop;

    if array_upper(properties.unassignments, 1) is not null then
      ret = ret || '  current.tags = current.tags - cast(' ||
	quote_nullable(cast(properties.unassignments as text)) || E' as text[]);\n';
    end if;

    ret = ret || E'end if;\n\n';

  stat.func = stat.func || ret;

  return stat;
end;
$$ language 'plpgsql' immutable;
