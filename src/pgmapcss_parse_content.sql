create or replace function pgmapcss_parse_content (
  /* content */ text
)
returns pgmapcss_compile_stat
as $$
#variable_conflict use_variable
declare
  r pgmapcss_selector;
  r1 record;
  selectors pgmapcss_selector[];
  properties pgmapcss_properties;
  content text;
  stat pgmapcss_compile_stat;
begin
  content:=$1;
  stat.selectors := Array[]::pgmapcss_selector[];
  stat.properties := Array[]::pgmapcss_properties[];
  stat.prop_types := ''::hstore;
  stat.prop_default_other := ''::hstore;
  stat.prop_values := ''::hstore;

  loop
    selectors:=Array[]::pgmapcss_selector[];

    r1 := pgmapcss_parse_defines(content, stat);
    content := r1.content;
    stat := r1.stat;

    for r in select * from pgmapcss_parse_selectors(content) loop
      selectors=array_append(selectors, r);
      content=substr(content, r.text_length);
    end loop;

    for properties in select * from pgmapcss_parse_properties(content) loop
      content := properties.content;
      properties.content := null;
    end loop;

    foreach r in array selectors loop
      stat.selectors := array_append(stat.selectors, r);
      stat.properties := array_append(stat.properties, properties);
    end loop;

    content := pgmapcss_parse_comments(content);

    if content is null or content ~ '^\s*$' then
      return stat;
    end if;
  end loop;

  return null;
end;
$$ language 'plpgsql' immutable;
