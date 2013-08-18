create or replace function pgmapcss_compile_statement (
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

    -- set values on 'current' for eval-statements
    if array_upper(avals(properties.eval_assignments), 1) is not null or
       array_upper(avals(properties.eval_properties), 1) is not null then
      ret = ret || '  current.pseudo_element_ind = ' || current_pseudo_element || E';\n';
    end if;

    -- set all properties which don't need eval
    ret = ret || '  current.styles[' || current_pseudo_element || '] = ' ||
      'current.styles[' || current_pseudo_element || '] || ' ||
      quote_nullable(cast(properties.properties as text)) || E';\n';

    -- set all tag assignments which don't need eval
    if array_upper(akeys(properties.assignments), 1) is not null then
      ret = ret || '  current.tags = current.tags || ' ||
	quote_nullable(cast(properties.assignments as text)) || E';\n';
    end if;

    -- set all eval-assignments on tags
    for r1 in select * from each(properties.eval_assignments) loop
      ret = ret || '  current.tags = current.tags || hstore(' ||
        quote_literal(r1.key) || ', ' || r1.value || E');\n';
    end loop;

    -- set all eval-assignments on properties
    for r1 in select * from each(properties.eval_properties) loop
      ret = ret || '  current.styles[' || current_pseudo_element || '] = ' ||
	'current.styles[' || current_pseudo_element || '] || hstore(' ||
        quote_literal(r1.key) || ', ' || r1.value || E');\n';
    end loop;

    -- unset tags
    if array_upper(properties.unassignments, 1) is not null then
      ret = ret || '  current.tags = current.tags - cast(' ||
	quote_nullable(cast(properties.unassignments as text)) || E' as text[]);\n';
    end if;

    -- set has_pseudo_element to true
    ret = ret || '  current.has_pseudo_element[' || current_pseudo_element || E'] = true;\n';

    ret = ret || E'end if;\n\n';

  stat.func = stat.func || ret;

  return stat;
end;
$$ language 'plpgsql' immutable;
