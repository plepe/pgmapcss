drop type if exists pgmapcss_properties_return cascade;
create type pgmapcss_properties_return as (
  properties            hstore,
  prop_list             hstore,
  assignments		hstore,
  unassignments		text[],
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
  assignment_type int;
begin
  content:=$1;

  ret.properties:=''::hstore;
  ret.prop_list:=''::hstore;
  ret.assignments:=''::hstore;
  ret.unassignments:=Array[]::text[];

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
      assignment_type=1;

      content=substring(content from '^[a-zA-Z0-9_-]+\s*:\s*(.*)$');

    elsif content ~ '^set\s+([a-zA-Z0-9_\-\.]+)\s*=' then
      key=substring(content from '^set\s+([a-zA-Z0-9_\-\.]+)\s*=');
      assignment_type=2;

      content=substring(content from '^set\s+[a-zA-Z0-9_\-\.]+\s*=\s*(.*)$');

    elsif content ~ '^set\s+([a-zA-Z0-9_\-\.]+)\s*;' then
      key=substring(content from '^set\s+([a-zA-Z0-9_\-\.]+)\s*;');
      assignment_type=2;

      content='yes;' || substring(content from '^set\s+[a-zA-Z0-9_\-\.]+\s*;(.*)$');

    elsif content ~ '^unset\s+([a-zA-Z0-9_\-\.]+)\s*;' then
      key=substring(content from '^unset\s+([a-zA-Z0-9_\-\.]+)\s*;');
      assignment_type=3;

      content='no;' || substring(content from '^unset\s+[a-zA-Z0-9_\-\.]+\s*;(.*)$');

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

      if assignment_type=1 then
	ret.properties=ret.properties||hstore(key, value);
	-- TODO: return type of value
	ret.prop_list=ret.prop_list||hstore(key, 'text');

      elsif assignment_type=2 then
	ret.assignments=ret.assignments||hstore(key, value);

      elsif assignment_type=3 then
	ret.unassignments=array_append(ret.unassignments, key);

      end if;

      content=substring(content from '^[^;]*;\s*(.*)$');
    else
      raise notice 'Error parsing prop value at "%..."', substring(content, 1, 40);
      return;
    end if;
  end loop;

  return;
end;
$$ language 'plpgsql' immutable;
