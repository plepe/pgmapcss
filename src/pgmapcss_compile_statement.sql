create or replace function pgmapcss_compile_statement (
  selector pgmapcss_selector,
  properties pgmapcss_properties,
  pgmapcss_compile_stat
)
returns pgmapcss_compile_stat
as $$
#variable_conflict use_variable
declare
  stat pgmapcss_compile_stat;
  ret text := ''::text;
  r pgmapcss_selector_part;
  r2 record;
  property record;
  current_pseudo_element text;
  t text;
  c text;
  prop_to_set hstore;
  tags_to_set hstore;
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

  prop_to_set := ''::hstore;
  tags_to_set := ''::hstore;

  -- set values on 'current' for eval-statements
  ret = ret || '  current.pseudo_element_ind = ' || current_pseudo_element || E';\n';

  foreach property in array properties.properties loop
    -- property assignment
    if property.assignment_type = 'P' then
      if property.eval_value is null then
	prop_to_set := prop_to_set || hstore(property.key, property.value);
	stat.properties_values := hstore_array_append_unique(
	  stat.properties_values, property.key, property.value);

      else
	ret = ret || pgmapcss_compile_statement_print_set(prop_to_set, tags_to_set, current_pseudo_element);
	prop_to_set := ''::hstore;
	tags_to_set := ''::hstore;

	ret = ret || '  current.styles[' || current_pseudo_element || '] = ' ||
	  'current.styles[' || current_pseudo_element || '] || hstore(' ||
	  quote_literal(property.key) || ', ' ||
	  pgmapcss_compile_eval(property.eval_value) || E');\n';

	stat.properties_values := hstore_array_append_unique(
	  stat.properties_values, property.key, '*');
      end if;

    -- tag assignment
    elsif property.assignment_type = 'T' then
      if property.eval_value is null then
	tags_to_set := tags_to_set || hstore(property.key, property.value);

      else
	ret = ret || pgmapcss_compile_statement_print_set(prop_to_set, tags_to_set, current_pseudo_element);
	prop_to_set := ''::hstore;
	tags_to_set := ''::hstore;

	ret = ret || '  current.tags = current.tags || hstore(' ||
	quote_literal(property.key) || ', ' ||
	pgmapcss_compile_eval(property.eval_value) || E');\n';
      end if;

    -- unset tags
    elsif property.assignment_type = 'U' then
      ret = ret || pgmapcss_compile_statement_print_set(prop_to_set, tags_to_set, current_pseudo_element);
      prop_to_set := ''::hstore;
      tags_to_set := ''::hstore;

      ret = ret || '  current.tags = current.tags - ' ||
        quote_literal(property.key) || E');\n';

    -- combine
    elsif property.assignment_type = 'C' then
      ret = ret || pgmapcss_compile_statement_print_set(prop_to_set, tags_to_set, current_pseudo_element);
      prop_to_set := ''::hstore;
      tags_to_set := ''::hstore;

      if property.eval_value is not null then
	c := pgmapcss_compile_eval(property.eval_value);
      else
	c := quote_nullable(property.value);
      end if;

      ret = ret || '  return query select object.id, current.tags, current.styles[' || current_pseudo_element || ']->''geo'', object.types, null::text, null::hstore, ' || quote_nullable(property.key) || E'::text, ' || c || E';\n';

    end if;
  end loop;

  ret = ret || pgmapcss_compile_statement_print_set(prop_to_set, tags_to_set, current_pseudo_element);

  -- set has_pseudo_element to true
  if r.create_pseudo_element then
    ret = ret || '  current.has_pseudo_element[' || current_pseudo_element || E'] = true;\n';
  end if;

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

create or replace function pgmapcss_compile_statement_print_set (
  prop_to_set hstore,
  tags_to_set hstore,
  current_pseudo_element text
)
returns text
as $$
#variable_conflict use_variable
declare
  ret text := ''::text;
begin
  if array_upper(akeys(prop_to_set), 1) is not null then
    ret = ret || '  current.styles[' || current_pseudo_element ||
      '] = ' || 'current.styles[' || current_pseudo_element || '] || ' ||
      quote_nullable(cast(prop_to_set as text)) || E';\n';
  end if;

  if array_upper(akeys(tags_to_set), 1) is not null then
    ret = ret || '  current.tags = current.tags || ' ||
      quote_nullable(cast(tags_to_set as text)) || E';\n';
  end if;

  return ret;
end;
$$ language 'plpgsql' immutable;
