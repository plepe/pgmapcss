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
  for i in select * from each(stat.prop_list) loop
    a = array_append(a, E'  ' || quote_ident(i.key) || E'\t' || i.value);
  end loop;
  ret = ret || array_to_string(a, E',\n');
  ret = ret || E'\n);\n\n';

  ret = ret || 'create or replace function css_check_' || style_id || E'(\n';
  ret = ret || E'  id\ttext,\n';
  ret = ret || E'  tags\thstore,\n';
  ret = ret || E'  way\tgeometry,\n';
  ret = ret || E'  type\ttext[],\n';
  ret = ret || E'  scale_denominator\tfloat\n';
  ret = ret || E') returns setof css_return_' || style_id || E' as $body$\n';
  ret = ret || E'declare\n';
  ret = ret || E'  styles hstore[];\n';
  ret = ret || E'  has_layer boolean[];\n';
  ret = ret || E'  ret css_return_' || style_id || E';\n';
  ret = ret || E'  layers text[] := ''' || cast(stat.layers as text) || E''';\n';
  ret = ret || E'  r record;\n';
  ret = ret || E'begin\n';
  ret = ret || E'  styles := array_fill(''''::hstore, Array[' || array_upper(stat.layers, 1) || E']);\n';
  ret = ret || E'  has_layer := array_fill(false, Array[' || array_upper(stat.layers, 1) || E']);\n';

  ret = ret || stat.func;

  ret = ret || E'  for r in select * from (select generate_series(1, ' || array_upper(stat.layers, 1) || E') i, unnest(styles) style) t order by coalesce(cast(style->''object-z-index'' as float), 0) asc loop\n';
  ret = ret || E'    if has_layer[r.i] then\n';
  ret = ret || E'      ret._style=styles[r.i];\n';
  ret = ret || E'      ret._layer=layers[r.i];\n';
  for i in select * from each(stat.prop_list) loop
    ret = ret || E'      ret.' || quote_ident(i.key) || ' = cast(ret._style->' || quote_literal(i.key) || E' as ' || quote_ident(i.value) || E');\n';
  end loop;
  ret = ret || E'      return next ret;\n';
  ret = ret || E'    end if;\n';
  ret = ret || E'  end loop;\n';

  ret = ret || E'  return;\n';
  ret = ret || E'end;\n$body$ language ''plpgsql'' immutable;\n';

  raise notice E'\n%\nproplist: %', ret, stat.prop_list;

  return ret;
end;
$$ language 'plpgsql' immutable;
