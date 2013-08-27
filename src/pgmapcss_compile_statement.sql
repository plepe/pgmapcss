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
  r2 record;
  current_pseudo_element text;
  t text;
  a text[];
begin
  stat := $3;

  r := selector.object;

  ret = ret || 'if   (';
  ret = ret || pgmapcss_compile_selector_part(selector.object);
  ret = ret || E')\nthen\n';

  -- if selector.link_parent then
  if (selector.link_condition).type != '' then
    ret = ret || E'parent_index := 0;\n';
    ret = ret || E'for parent_object in ' || pgmapcss_compile_link_selector(selector) || E' loop\n';
    ret = ret || E'parent_index := parent_index + 1;\n';
    ret = ret || E'o.tags := parent_object.link_tags || hstore(''index'', cast(parent_index as text));\n';
    ret = ret || E'if (' || pgmapcss_compile_conditions((selector.link_condition).conditions, 'o.') || E') then\n';
    ret = ret || E'current.parent_object = parent_object;\n';
    ret = ret || E'current.link_object = o;\n';
  end if;

  -- if we find a pseudo element '*' then iterate over all possible
  -- pseudo elements
  if r.pseudo_element = '*' then
    current_pseudo_element = 'i';
    ret = ret || E'for i in 1..array_upper(current.pseudo_elements, 1) loop\n';

  -- otherwise we just search the index of the current pseudo element
  else
    current_pseudo_element = array_search(r.pseudo_element, stat.pseudo_elements);
    if current_pseudo_element is null then
      stat.pseudo_elements = array_append(stat.pseudo_elements, r.pseudo_element);
      current_pseudo_element = array_upper(stat.pseudo_elements, 1);
    end if;
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

    -- remember all possible property values
    for r1 in select * from each(properties.properties) loop
      t := stat.properties_values->(r1.key);
      if t is null then
	a := Array[]::text[];
      else
	a := cast(t as text[]);
      end if;

      if array_search(r1.value, a) is null then
	stat.properties_values = stat.properties_values || hstore(r1.key, cast(
	  array_append(a, r1.value) as text));
      end if;
    end loop;

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

      -- remember all possible property values
      t := stat.properties_values->(r1.key);
      if t is null then
	a := Array[]::text[];
      else
	a := cast(t as text[]);
      end if;

      if array_search('*', a) is null then
	stat.properties_values = stat.properties_values || hstore(r1.key, cast(
	  array_append(a, '*') as text));
      end if;
    end loop;

    -- unset tags
    if array_upper(properties.unassignments, 1) is not null then
      ret = ret || '  current.tags = current.tags - cast(' ||
	quote_nullable(cast(properties.unassignments as text)) || E' as text[]);\n';
    end if;

    -- set has_pseudo_element to true
    if r.create_pseudo_element then
      ret = ret || '  current.has_pseudo_element[' || current_pseudo_element || E'] = true;\n';
    end if;

    -- if we combine this feature with other features, return
    for r1 in select * from each(properties.combine) loop
      ret = ret || '  return query select object.id, current.tags, current.styles[' || current_pseudo_element || ']->''geo'', object.types, null::text, null::hstore, ' || quote_nullable(r1.key) || E'::text, ' || r1.value || E';\n';
    end loop;

  if r.pseudo_element = '*' then
    ret = ret || E'end loop;\n';
  end if;

  if (selector.link_condition).type != '' then
    ret = ret || E'end if;\n';
    ret = ret || E'end loop;\n';
    ret = ret || E'current.parent_object = null;\n';
  end if;

  ret = ret || E'end if;\n\n';

  stat.func = stat.func || ret;

  return stat;
end;
$$ language 'plpgsql' immutable;
