create or replace function pgmapcss_parse_content (
  /* content */ text
)
returns pgmapcss_compile_stat
as $$
#variable_conflict use_variable
declare
  r pgmapcss_selector;
  selectors pgmapcss_selector[];
  properties pgmapcss_rule_properties;
  content text;
  stat pgmapcss_compile_stat;
begin
  content:=$1;
  stat.selectors := Array[]::pgmapcss_selector[];
  stat.properties := Array[]::pgmapcss_rule_properties[];
  stat.prop_list := ''::hstore;

  loop
    selectors:=Array[]::pgmapcss_selector[];

    for r in select * from pgmapcss_parse_selectors(content) loop
      selectors=array_append(selectors, r);
      content=substr(content, r.text_length);
    end loop;

    for properties in select * from pgmapcss_parse_properties(content) loop
      content=substr(content, properties.text_length);
      stat.prop_list=stat.prop_list || properties.prop_types;
    end loop;

    foreach r in array selectors loop
      stat.selectors := array_append(stat.selectors, r);
      stat.properties := array_append(stat.properties, properties);
    end loop;

    if content is null or content ~ '^\s*$' then
      return stat;
    end if;
  end loop;

  return null;
end;
$$ language 'plpgsql' immutable;
