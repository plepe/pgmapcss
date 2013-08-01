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
  stat := pgmapcss_compile_content($2);

  ret = ret || 'drop type if exists css_return_' || style_id || E' cascade;\n';
  ret = ret || 'create type css_return_' || style_id || E' as (\n';

  a = Array[]::text[];
  a = array_append(a, E'  _style\thstore');
  a = array_append(a, E'  _layer\ttext');
  a = array_append(a, E'  _geo\ttext');
  a = array_append(a, E'  _tags\thstore');
  for i in select * from each(stat.prop_list) loop
    a = array_append(a, E'  ' || quote_ident(i.key) || E'\t' || i.value);
  end loop;
  ret = ret || array_to_string(a, E',\n');
  ret = ret || E'\n);\n\n';

  ret = ret || 'create or replace function css_check_' || style_id || E'(\n';
  ret = ret || E'  object\tpgmapcss_object,\n';
  ret = ret || E'  render_context\tpgmapcss_render_context\n';
  ret = ret || E') returns setof css_return_' || style_id || E' as $body$\n';
  ret = ret || E'declare\n';
  ret = ret || E'  current pgmapcss_current;\n';
  ret = ret || E'  ret css_return_' || style_id || E';\n';
  ret = ret || E'  layers text[] := ''' || cast(stat.layers as text) || E''';\n';
  ret = ret || E'  r record;\n';
  ret = ret || E'begin\n';
  ret = ret || E'  current.tags := object.tags;\n';
  ret = ret || E'  current.styles := array_fill(''''::hstore, Array[' || array_upper(stat.layers, 1) || E']);\n';
  ret = ret || E'  current.has_layer := array_fill(false, Array[' || array_upper(stat.layers, 1) || E']);\n';
  ret = ret || E'  ret._geo := object.geo;\n';

  ret = ret || stat.func;

  ret = ret || E'  ret._tags=current.tags;\n';
  ret = ret || E'  for r in select * from (select generate_series(1, ' || array_upper(stat.layers, 1) || E') i, unnest(current.styles) style) t order by coalesce(cast(style->''object-z-index'' as float), 0) asc loop\n';
  ret = ret || E'    if current.has_layer[r.i] then\n';
  ret = ret || E'      ret._style=current.styles[r.i];\n';
  ret = ret || E'      ret._layer=layers[r.i];\n';
  for i in select * from each(stat.prop_list) loop
    ret = ret || E'      ret.' || quote_ident(i.key) || ' = cast(ret._style->' || quote_literal(i.key) || E' as ' || quote_ident(i.value) || E');\n';
  end loop;
  ret = ret || E'      return next ret;\n';
  ret = ret || E'    end if;\n';
  ret = ret || E'  end loop;\n';

  ret = ret || E'  return;\n';
  ret = ret || E'end;\n$body$ language ''plpgsql'' immutable;\n';

  return ret;
end;
$$ language 'plpgsql' immutable;
