create or replace function pgmapcss_compile_content (
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
  stat.func :=''::text;
  stat.prop_list := ''::hstore;
  stat.pseudo_elements := Array['default']::text[];

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

    -- TODO: make list of match-relevant tags configurable
    if properties.prop_has_value ?| Array['text', 'width', 'fill-color'] then
      stat.where_selectors := array_cat(stat.where_selectors, selectors);
    end if;

    stat := pgmapcss_build_statement(selectors, properties, stat);

    if content is null or content ~ '^\s*$' then
      return stat;
    end if;
  end loop;

  return null;
end;
$$ language 'plpgsql' immutable;
