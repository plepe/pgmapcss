create or replace function pgmapcss_compile (
  style_id      text,
  /* content */ text
)
returns text
as $$
#variable_conflict use_variable
declare
  content text;
  ret text:=''::text;
  stat		pgmapcss_compile_stat;
  i record;
  a text[];
begin
  stat := pgmapcss_parse_content($2);
  stat := pgmapcss_compile_content(stat);

  -- Remove all old functions / data types
  ret = ret || 'drop type if exists ' || style_id || E'_result cascade;\n';

  -- create result type for style
  ret = ret || 'create type ' || style_id || E'_result as (\n';

  a = Array[]::text[];
  a = array_append(a, E'  _id\ttext');
  a = array_append(a, E'  _tags\thstore');
  a = array_append(a, E'  _geo\ttext');
  a = array_append(a, E'  _types\ttext[]');
  a = array_append(a, E'  _pseudo_element\ttext');
  a = array_append(a, E'  _properties\thstore');
  for i in select * from each(stat.prop_list) loop
    a = array_append(a, E'  ' || quote_ident(i.key) || E'\t' || i.value);
  end loop;
  ret = ret || array_to_string(a, E',\n');
  ret = ret || E'\n);\n\n';

  -- function to check a single object
  ret = ret || 'create or replace function ' || style_id || E'_check(\n';
  ret = ret || E'  object\tpgmapcss_object,\n';
  ret = ret || E'  render_context\tpgmapcss_render_context\n';
  ret = ret || E') returns setof pgmapcss_result as $body$\n';
  ret = ret || E'declare\n';
  ret = ret || E'  current pgmapcss_current;\n';
  ret = ret || E'  ret pgmapcss_result;\n';
  ret = ret || E'  r record;\n';
  ret = ret || E'  parent_object record;\n';
  ret = ret || E'  parent_index int;\n';
  ret = ret || E'  o pgmapcss_object;\n';
  ret = ret || E'  i int;\n';
  ret = ret || E'begin\n';
  ret = ret || E'  current.pseudo_elements := ''' || cast(stat.pseudo_elements as text) || E''';\n';
  ret = ret || E'  current.tags := object.tags;\n';
  ret = ret || E'  current.types := object.types;\n';
  -- initialize all styles with the 'geo' property
  ret = ret || E'  current.styles := array_fill(hstore(''geo'', object.geo), Array[' || array_upper(stat.pseudo_elements, 1) || E']);\n';
  ret = ret || E'  current.has_pseudo_element := array_fill(false, Array[' || array_upper(stat.pseudo_elements, 1) || E']);\n';

  ret = ret || stat.func;

  ret = ret || E'  ret.id=object.id;\n';
  ret = ret || E'  ret.types=object.types;\n';
  ret = ret || E'  ret.tags=current.tags;\n';
  ret = ret || E'  for r in select * from (select generate_series(1, ' || array_upper(stat.pseudo_elements, 1) || E') i, unnest(current.styles) style) t order by coalesce(cast(style->''object-z-index'' as float), 0) asc loop\n';
  ret = ret || E'    if current.has_pseudo_element[r.i] then\n';
  ret = ret || E'      ret.geo=current.styles[r.i]->''geo'';\n';
  ret = ret || E'      current.styles[r.i] := current.styles[r.i] - ''geo''::text;\n';
  ret = ret || E'      ret.properties=current.styles[r.i];\n';
  ret = ret || E'      ret.pseudo_element=(current.pseudo_elements)[r.i];\n';
  ret = ret || E'      return next ret;\n';
  ret = ret || E'    end if;\n';
  ret = ret || E'  end loop;\n';

  ret = ret || E'  return;\n';
  ret = ret || E'end;\n$body$ language ''plpgsql'' immutable;\n';

  -- function to get WHERE clause for efficient index usage for current
  -- render context
  ret = ret || E';\n';
  ret = ret || E'create or replace function ' || style_id || E'_get_where(\n';
  ret = ret || E'  render_context\tpgmapcss_render_context\n';
  ret = ret || E') returns hstore as $body$\n';
  ret = ret || E'declare\n';
  ret = ret || E'  ret ' || style_id || E'_result;\n';
  ret = ret || E'begin\n';
  ret = ret || pgmapcss_compile_where(stat);
  ret = ret || E'end;\n$body$ language ''plpgsql'' immutable;\n';

  -- function to match objects in bbox
  ret = ret || E';\n';
  ret = ret || E'create or replace function ' || style_id || E'_match(\n';
  ret = ret || E'  render_context\tpgmapcss_render_context\n';
  ret = ret || E') returns setof ' || style_id || E'_result as $body$\n';
  ret = ret || E'declare\n';
  ret = ret || E'  ret ' || style_id || E'_result;\n';
  ret = ret || E'begin\n';
  ret = ret || E'  return query \n';
  ret = ret || E'    select \n';
  ret = ret || E'      id, tags, geo, types, pseudo_element, properties';
  for i in select * from each(stat.prop_list) loop
    ret = ret || E',\n      cast(properties->' || quote_literal(i.key) || E' as ' || quote_ident(i.value) || E')';
  end loop;
  ret = ret || E'    from\n';
  ret = ret || E'    (select (result).* from\n';
  ret = ret || E'      (select\n';
  ret = ret || E'        (CASE WHEN (result).combine_type is null THEN (array_agg(result))[1]\n';
  ret = ret || E'        ELSE ' || style_id || E'_check(\n';
  ret = ret || E'          pgmapcss_object(string_agg((result).id, '';''), hstore_merge(array_agg((result).tags)), ST_Collect((result).geo), Array[(result).combine_type]), render_context)\n';
  ret = ret || E'        END) result from\n';
  ret = ret || E'      (select\n';
  ret = ret || E'        ' || style_id || E'_check(\n';
  ret = ret || E'          object, render_context\n';
  ret = ret || E'        ) result\n';
  ret = ret || E'      from\n';
  ret = ret || E'        objects(render_context, ' || style_id || E'_get_where(render_context)) object\n';
  ret = ret || E'      offset 0) t\n';
  ret = ret || E'      group by (result).combine_type, coalesce((result).combine_id, (result).id || (result).pseudo_element) offset 0) t) t\n';
  ret = ret || E'      order by coalesce(cast(properties->''z-index'' as float), 0) asc;\n\n';
  ret = ret || E'  return;\n';
  ret = ret || E'end;\n$body$ language ''plpgsql'' immutable;\n';

  stat.func := '';
  -- save stat as function
  ret = ret || E';\n';
  ret = ret || E'create or replace function ' || style_id || E'_stat(\n';
  ret = ret || E') returns pgmapcss_compile_stat as $body$\n';
  ret = ret || E'declare\n';
  ret = ret || E'  ret pgmapcss_compile_stat;\n';
  ret = ret || E'begin\n';
  ret = ret || E'  ret := cast(' || quote_nullable(stat) || E' as pgmapcss_compile_stat);\n';
  ret = ret || E'  return ret;\n';
  ret = ret || E'end;\n$body$ language ''plpgsql'' immutable;\n';

  return ret;
end;
$$ language 'plpgsql' immutable;
