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
begin
  r := pgmapcss_compile_content($2);

  ret = ret || r.func;

  raise notice E'\n%\nproplist: %', ret, r.prop_list;

  return ret;
end;
$$ language 'plpgsql' immutable;

select pgmapcss_compile('foo', E'way|z11-14[highway=primary][access=public]:closed::layer1,\nnode { foo: bar; test: text; } way[x=y]{ foo: b''ar; }');
