create or replace function pgmapcss_parse_defines (
  /* content */ IN text,
  IN pgmapcss_compile_stat,
  OUT content text,
  OUT stat pgmapcss_compile_stat
)
returns record
as $$
#variable_conflict use_variable
declare
  m text;
  m1 text;
  r record;
begin
  content := $1;
  stat := $2;

  loop
    content := pgmapcss_parse_comments(content);

    if content ~ '^\s*@type' then
      m := substring(content from '\s*@type\s+([^\s]+)\s+([^\s]+)\s*;');
      m1 := substring(content from '\s*@type\s+(?:[^\s]+)\s+([^\s]+)\s*;');
      content := substring(content from '\s*@type\s+(?:[^\s]+)\s+(?:[^\s]+)\s*;(.*)$');

      stat.prop_types := stat.prop_types || hstore(m, m1);

    elsif content ~ '^\s*@default_other' then
      m := substring(content from '\s*@default_other\s+([^\s]+)\s+([^\s]+)\s*;');
      m1 := substring(content from '\s*@default_other\s+(?:[^\s]+)\s+([^\s]+)\s*;');
      content := substring(content from '\s*@default_other\s+(?:[^\s]+)\s+(?:[^\s]+)\s*;(.*)$');

      stat.prop_default_other := stat.prop_default_other || hstore(m, m1);

    elsif content ~ '^\s*@values' then
      m := substring(content from '\s*@values\s+([^\s]+)\s+([^\s]+)\s*;');
      m1 := substring(content from '\s*@values\s+(?:[^\s]+)\s+([^\s]+)\s*;');
      content := substring(content from '\s*@values\s+(?:[^\s]+)\s+(?:[^\s]+)\s*;(.*)$');

      stat.prop_values := stat.prop_values || hstore(m, m1);

    elsif content ~ '^\s*@postprocess' then
      m := substring(content from '\s*@postprocess\s+([^\s]+)\s+([^;]+)\s*;');
      m1 := substring(content from '\s*@postprocess\s+(?:[^\s]+)\s+([^;]+)\s*;');
      content := substring(content from '\s*@postprocess\s+(?:[^\s]+)\s+(?:[^;]+)\s*;(.*)$');

      r := pgmapcss_parse_eval(m1);

      stat.prop_postprocess := stat.prop_postprocess || hstore(m, r.result);

    elsif content ~ '^\s*@depend_property' then
      m := substring(content from '\s*@depend_property\s+([^\s]+)\s+([^\s]+)\s*;');
      m1 := substring(content from '\s*@depend_property\s+(?:[^\s]+)\s+([^\s]+)\s*;');
      content := substring(content from '\s*@depend_property\s+(?:[^\s]+)\s+(?:[^\s]+)\s*;(.*)$');
      m1 := cast(string_to_array(m1, ',') as text);

      stat.prop_depend := stat.prop_depend || hstore(m, m1);

    elsif content ~ '^\s*@style_element_property' then
      m := substring(content from '\s*@style_element_property\s+([^\s]+)\s+([^\s]+)\s*;');
      m1 := substring(content from '\s*@style_element_property\s+(?:[^\s]+)\s+([^\s]+)\s*;');
      content := substring(content from '\s*@style_element_property\s+(?:[^\s]+)\s+(?:[^\s]+)\s*;(.*)$');
      m1 := cast(string_to_array(m1, ',') as text);

      stat.prop_style_element := stat.prop_style_element || hstore(m, m1);

    -- ignore unknown @-statements
    elsif content ~ '^\s*@[^;]*;' then
      m := substring(content from '^\s*(@[^;]*;)');
      content := substring(content from '^\s*@[^;]*;(.*)');

      raise notice 'Ignoring statement "%"', m;

    else
      return;

    end if;
  end loop;

  return;
end;
$$ language 'plpgsql' immutable;
