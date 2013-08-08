drop function if exists pgmapcss_parse_properties(text);
create or replace function pgmapcss_parse_properties (
  text
)
returns setof pgmapcss_rule_properties
as $$
#variable_conflict use_variable
declare
  ret pgmapcss_rule_properties;
  content text;
  m text;
  key text;
  value text;
  assignment_type int;
  r record;
  r1 record;
begin
  content:=$1;

  ret.properties:=''::hstore;
  ret.prop_list:=''::hstore;
  ret.assignments:=''::hstore;
  ret.unassignments:=Array[]::text[];
  ret.eval_assignments:=''::hstore;
  ret.eval_properties:=''::hstore;

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
    if content ~ '^\s*([a-zA-Z0-9_-]+)\s*:' then
      key=substring(content from '^\s*([a-zA-Z0-9_-]+)\s*:');
      assignment_type=1;

      content=substring(content from '^\s*[a-zA-Z0-9_-]+\s*:\s*(.*)$');

    elsif content ~ '^\s*set\s+([a-zA-Z0-9_\-\.]+)\s*=' then
      key=substring(content from '^\s*set\s+([a-zA-Z0-9_\-\.]+)\s*=');
      assignment_type=2;

      content=substring(content from '^\s*set\s+[a-zA-Z0-9_\-\.]+\s*=\s*(.*)$');

    elsif content ~ '^\s*set\s+([a-zA-Z0-9_\-\.]+)\s*;' then
      key=substring(content from '^\s*set\s+([a-zA-Z0-9_\-\.]+)\s*;');
      assignment_type=2;

      content='yes;' || substring(content from '^\s*set\s+[a-zA-Z0-9_\-\.]+\s*;(.*)$');

    elsif content ~ '^\s*unset\s+([a-zA-Z0-9_\-\.]+)\s*;' then
      key=substring(content from '^\s*unset\s+([a-zA-Z0-9_\-\.]+)\s*;');
      assignment_type=3;

      content='no;' || substring(content from '^\s*unset\s+[a-zA-Z0-9_\-\.]+\s*;(.*)$');

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

      if assignment_type = 1 then
	ret.eval_properties := ret.eval_properties || hstore(key, pgmapcss_compile_eval(r.result));
	ret.prop_list := ret.prop_list||hstore(key, 'text');
      elsif assignment_type = 2 then
	ret.eval_assignments := ret.eval_assignments || hstore(key, pgmapcss_compile_eval(r.result));
      end if;

      content := substring(content, 6 + r.text_length);
      content := substring(content from '^[^;]*;\s*(.*)$');
    elsif content ~ '^([^;]*);' then
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

      -- check for comments
      content := pgmapcss_parse_comments(content);

    else
      raise notice 'Error parsing prop value at "%..."', substring(content, 1, 40);
      return;
    end if;
  end loop;

  return;
end;
$$ language 'plpgsql' immutable;
