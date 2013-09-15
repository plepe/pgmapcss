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
  ta text[];
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
      ret.content := substring(content from '^\s*}(.*)$');

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

    elsif content ~ '^rgb\(' then
      m := substring(content from '^rgb\(([0-9\.,%\s]+)\)');

      ta := string_to_array(m, ',');
      if array_upper(ta, 1) != 3 then
	raise notice 'Error parsing rgb() value: "%"', m;
      else
	for r in 1..3 loop
	  if ta[r] ~ '^\s*([0-9]+)\s*$' then
	    ta[r] := lpad(to_hex(cast(ta[r] as int)), 2, '0');
	  elsif ta[r] ~ '^\s*([0-9]+\.[0-9]+)\s*$' then
	    ta[r] := lpad(to_hex(cast(cast(ta[r] as float) * 255 as int)), 2, '0');
	  elsif ta[r] ~ '^\s*([0-9]+(\.[0-9]+)?)%\s*$' then
	    m := substring(ta[r] from '^\s*([0-9]+(\.[0-9]+)?)%\s*$');
	    ta[r] := lpad(to_hex(cast(cast(m as float) * 2.55 as int)), 2, '0');
	  else
	    raise notice 'Can''t parse rgb() value: "%"', ta[r];
	  end if;
	end loop;

	ret1.value := '#' || array_to_string(ta, '');
      end if;

      content := substring(content from '^rgb\((?:[0-9\.,%\s]+)\)\s*;(.*)$');
    elsif r is not null then
    -- value is enclosed in quotes
      ret1.value := r.result;

      content := substring(content, r.text_length + 1);
      content := substring(content from '^\s*;\s*(.*)$');

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

    else
      raise notice 'Error parsing prop value at "%..."', substring(content, 1, 40);
      return;
    end if;

    -- check for comments
    content := pgmapcss_parse_comments(content);

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
