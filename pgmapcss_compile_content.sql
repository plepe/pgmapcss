drop type if exists pgmapcss_compile_content_return cascade;
create type pgmapcss_compile_content_return as (
  func          text,
  prop_list     hstore
);

create or replace function pgmapcss_compile_content (
  /* content */ text
)
returns pgmapcss_compile_content_return
as $$
#variable_conflict use_variable
declare
  r pgmapcss_selector_return;
  selectors pgmapcss_selector_return[];
  properties pgmapcss_properties_return;
  content text;
  ret pgmapcss_compile_content_return;
begin
  content:=$1;
  ret.func :=''::text;
  ret.prop_list := ''::hstore;

  loop
    selectors:=Array[]::pgmapcss_selector_return[];

    for r in select * from pgmapcss_parse_selectors(content) loop
      selectors=array_append(selectors, r);
      content=substr(content, r.text_length);
    end loop;

    for properties in select * from pgmapcss_parse_properties(content) loop
      content=substr(content, properties.text_length);
      ret.prop_list=ret.prop_list || properties.prop_list;
    end loop;

    ret.func = ret.func || pgmapcss_build_statement(selectors, properties);

    if content is null or content ~ '^\s*$' then
      return ret;
    end if;
  end loop;

  return null;
end;
$$ language 'plpgsql' immutable;
