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
