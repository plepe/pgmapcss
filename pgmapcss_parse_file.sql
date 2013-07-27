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
  properties pgmapcss_properties_return;
  content text;
begin
  content:=$2;

  loop
    selectors:=Array[]::pgmapcss_selector_return[];

    for r in select * from pgmapcss_parse_selectors(content) loop
      selectors=array_append(selectors, r);
      raise notice '%', r;
      content=substr(content, r.text_length);
    end loop;

    for properties in select * from pgmapcss_parse_properties(content) loop
      raise notice '%', properties;

      content=substr(content, properties.text_length);
    end loop;

    raise notice 'content: %', content;
    if content is null or content ~ '^\s*$' then
      return true;
    end if;
  end loop;

  return false;
end;
$$ language 'plpgsql' immutable;

select pgmapcss_parse_file('foo', E'way|z11-14[highway=primary][access=public]:closed::layer1,\nnode { foo: bar; test: text; } way[x=y]{ foo: bar; }');
