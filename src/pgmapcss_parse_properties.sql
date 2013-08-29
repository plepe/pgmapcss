drop function if exists pgmapcss_parse_properties(text);
create or replace function pgmapcss_parse_properties (
  text
)
returns setof pgmapcss_properties
as $$
#variable_conflict use_variable
declare
  ret pgmapcss_properties;
  ret1 pgmapcss_property;
  content text;
  m text;
  r record;
  r1 record;
begin
  content:=$1;

  ret.properties := Array[]::pgmapcss_property[];
  ret.prop_types := ''::hstore;
  ret.prop_has_value := ''::hstore;
  ret.has_combine := false;

  -- check for comments
  content := pgmapcss_parse_comments(content);

  m=substring(content from '^[^{]*{\s*(.*)');
  if m is null then
    raise notice 'Error parsing at "%..."', substring(content, 1, 40);
    return;
  else
    content=m;
  end if;

  -- check for comments
  content := pgmapcss_parse_comments(content);

  loop
    ret1.assignment_type := null;
    ret1.key := null;
    ret1.value := null;
    ret1.eval_value := null;
    ret1.unit := null;

    if content ~ '^\s*([a-zA-Z0-9_-]+)\s*:' then
      ret1.key := substring(content from '^\s*([a-zA-Z0-9_-]+)\s*:');
      ret1.assignment_type := 'P';

      content=substring(content from '^\s*[a-zA-Z0-9_-]+\s*:\s*(.*)$');

    elsif content ~ '^\s*set\s+([a-zA-Z0-9_\-\.]+)\s*=' then
      ret1.key := substring(content from '^\s*set\s+([a-zA-Z0-9_\-\.]+)\s*=');
      ret1.assignment_type := 'T';

      content=substring(content from '^\s*set\s+[a-zA-Z0-9_\-\.]+\s*=\s*(.*)$');

    elsif content ~ '^\s*set\s+([a-zA-Z0-9_\-\.]+)\s*;' then
      ret1.key := substring(content from '^\s*set\s+([a-zA-Z0-9_\-\.]+)\s*;');
      ret1.assignment_type := 'T';

      content='yes;' || substring(content from '^\s*set\s+[a-zA-Z0-9_\-\.]+\s*;(.*)$');

    elsif content ~ '^\s*unset\s+([a-zA-Z0-9_\-\.]+)\s*;' then
      ret1.key := substring(content from '^\s*unset\s+([a-zA-Z0-9_\-\.]+)\s*;');
      ret1.assignment_type := 'U';

      content=';' || substring(content from '^\s*unset\s+[a-zA-Z0-9_\-\.]+\s*;(.*)$');

    elsif content ~ '^\s*combine\s+([a-zA-Z0-9_\-\.]+)\s+' then
      ret1.key := substring(content from '^\s*combine\s+([a-zA-Z0-9_\-\.]+)\s+');
      ret1.assignment_type := 'C';
      ret.has_combine := true;

      content=substring(content from '^\s*combine\s+[a-zA-Z0-9_\-\.]+\s+(.*)$');

    elsif content ~ '^\s*}' then
      ret.text_length=strpos($1, content)+1;

      return next ret;
      return;
    else
      raise notice 'Error parsing prop key at "%..."', substring(content, 1, 40);
      return;
    end if;

    -- check for comments
    content := pgmapcss_parse_comments(content);
    r := pgmapcss_parse_string(content);

    if content ~ '^eval\(' then
      r1 := pgmapcss_parse_string(content, null, 6);
      if r1.result is not null then
        if substring(content, 6 + r1.text_length) ~ '^\s*\)\s*;' then
	  r := pgmapcss_parse_eval(r1.result);

	  r.text_length := r1.text_length;
	end if;
      else
	r := pgmapcss_parse_eval(content, 6);
      end if;

      if r.result is null then
	raise notice 'error parsing eval-statement at "%..."', substring(content, 1, 40);
	return;
      end if;

      ret1.eval_value := r.result;

      content := substring(content, 6 + r.text_length);
      content := substring(content from '^[^;]*;\s*(.*)$');

    elsif r is not null then
    -- value is enclosed in quotes
      ret1.value := r.result;

      content := substring(content, r.text_length + 1);
      content := substring(content from '^\s*;\s*(.*)$');

      -- check for comments
      content := pgmapcss_parse_comments(content);

    elsif content ~ '^([^;]*);' then
      ret1.value := rtrim(substring(content from '^([^;]*);'));

      if ret1.value = '' then
	ret1.value := null;

      elsif ret1.value ~ '^(.*)(px|m|u)$' then
	ret1.unit := substring(ret1.value from '^(?:.*)(px|m|u)');

	-- no need to calculate pixel values
	if ret1.unit = 'px' then
	  ret1.value := substring(ret1.value from '^(.*)px');

	-- prepare an eval function to convert unit to pixel values
	else
	  ret1.eval_value := pgmapcss_parse_eval('number("' || ret1.value || '")');
	  ret1.value := null;
	end if;
      end if;

      content=substring(content from '^[^;]*;\s*(.*)$');

      -- check for comments
      content := pgmapcss_parse_comments(content);

    else
      raise notice 'Error parsing prop value at "%..."', substring(content, 1, 40);
      return;
    end if;

    if ret1.assignment_type = 'P' then
      -- TODO: return type of value
      ret.prop_types := ret.prop_types || hstore(ret1.key, 'text');
      if ((ret1.value != '') and (ret1.value is not null)) or
	  (ret1.eval_value is not null) then
	ret.prop_has_value := ret.prop_has_value || hstore(ret1.key, '1');
      end if;
    end if;

    ret.properties := array_append(ret.properties, ret1);
  end loop;

  return;
end;
$$ language 'plpgsql' immutable;
