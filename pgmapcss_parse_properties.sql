drop type if exists pgmapcss_properties_return cascade;
create type pgmapcss_properties_return as (
  properties            hstore,
  text_length           int
);

drop function pgmapcss_parse_properties(text);
create or replace function pgmapcss_parse_properties (
  text
)
returns setof pgmapcss_properties_return
as $$
#variable_conflict use_variable
declare
  ret pgmapcss_properties_return;
  content text;
  m text;
  key text;
  value text;
begin
  content:=$1;

  ret.properties:=''::hstore;

  m=substring(content from '^[^{]*{\s*(.*)');
  if m is null then
    raise notice 'Error parsing at "%..."', substring(content, 1, 40);
    return;
  else
    content=m;
  end if;

  loop
    if content ~ '^([a-zA-Z0-9_-]+)\s*:' then
      key=substring(content from '^([a-zA-Z0-9_-]+)\s*:');

      content=substring(content from '^[a-zA-Z0-9_-]+\s*:\s*(.*)$');

    elsif content ~ '^}' then
      ret.text_length=strpos($1, content)+1;

      return next ret;
      return;
    else
      raise notice 'Error parsing prop key at "%..."', substring(content, 1, 40);
      return;
    end if;

    if content ~ '^([^;]*);' then
      value=substring(content from '^([^;]*);');
      ret.properties=ret.properties||hstore(key, value);

      content=substring(content from '^[^;]*;\s*(.*)$');
    else
      raise notice 'Error parsing prop value at "%..."', substring(content, 1, 40);
      return;
    end if;
  end loop;

  return;
end;
$$ language 'plpgsql' immutable;
