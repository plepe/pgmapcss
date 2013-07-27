create or replace function pgmapcss_parse_file (
  style_id      text,
  /* content */ text
)
returns boolean
as $$
#variable_conflict use_variable
declare
  r pgmapcss_selector_return;
  selectors pgmapcss_selector_return[];
  content text;
begin
  content:=$2;

    selectors:=Array[]::pgmapcss_selector_return[];

    for r in select * from pgmapcss_parse_selectors(content) loop
      selectors=array_append(selectors, r);
      raise notice '%', r;
      content=substr(content, r.text_length);
    end loop;

    raise notice 'content: %', content;

  return true;
end;
$$ language 'plpgsql' immutable;

select pgmapcss_parse_file('foo', E'way|z11-14[highway=primary][access=public]:closed::layer1,\nnode { foo: bar; test: text; } bla { foo: bar; }');
