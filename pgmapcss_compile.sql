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
  r pgmapcss_compile_statements_return;
  i record;
  a text[];
begin
  r := pgmapcss_compile_content($2);

  ret = ret || 'drop type css_return_' || style_id || E' cascade;\n';
  ret = ret || 'create type css_return_' || style_id || E' as (\n';

  a = Array[]::text[];
  a = array_append(a, E'  _style\thstore');
  for i in select * from each(r.prop_list) loop
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
  ret = ret || E'  style hstore := ''''::hstore;\n';
  ret = ret || E'  ret css_return_' || style_id || E';\n';
  ret = ret || E'begin\n';

  ret = ret || r.func;

  ret = ret || E'  ret._style=style;\n';
  for i in select * from each(r.prop_list) loop
    ret = ret || E'  ret.' || quote_ident(i.key) || ' = cast(style->' || quote_literal(i.key) || E' as ' || quote_ident(i.value) || E');\n';
  end loop;

  ret = ret || E'  return next ret;\n';
  ret = ret || E'  return;\n';
  ret = ret || E'end;\n$body$ language ''plpgsql'' immutable;\n';

  raise notice E'\n%\nproplist: %', ret, r.prop_list;

  return ret;
end;
$$ language 'plpgsql' immutable;

select pgmapcss_compile('foo', E'way|z11-14[highway=primary][access=public]:closed::layer1,\nnode { foo: bar; test: text; } way[x=y]{ foo: b''ar; line-width: 3; }');
