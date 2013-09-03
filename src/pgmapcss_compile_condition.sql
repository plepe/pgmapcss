drop function if exists pgmapcss_compile_condition(pgmapcss_condition);
create or replace function pgmapcss_compile_condition(
  pgmapcss_condition,
  prefix	text	default '',
  match_where boolean default false
)
returns text
as $$
#variable_conflict use_variable
declare
  ret text := '';
  condition pgmapcss_condition;
  m text;
  final_value text;
begin
  condition := $1;

  if condition.value_type = 0 then
    final_value := quote_literal(condition.value);
  elsif condition.value_type = 1 then
    final_value := pgmapcss_compile_eval(condition.value);
  end if;

  -- when compiling for get_where()
  if match_where then
    if condition.value_type = 1 then
      if condition.op ~ '^! ' then
	return 'true';
      else
	return prefix || 'tags ? ' || quote_literal(condition.key);
      end if;
    end if;
  end if;

  -- !
  if condition.op ~ '^! ' then
    ret := ret || 'not ';
    condition.op := substring(condition.op, 3);
  end if;

  -- has_condition.key
  if condition.op = 'has_tag' then
    ret := ret || prefix || 'tags ? ' || quote_literal(condition.key);

  -- =
  elsif condition.op = '=' then
    if condition.value_type = 0 then
      ret := ret || prefix || 'tags @> ''' || quote_ident(condition.key) || '=>' || quote_ident(condition.value) || '''';
    else
      ret := ret || prefix || 'tags->' || quote_literal(condition.key) || ' = ' || final_value;
    end if;

  -- !=
  elsif condition.op = '!=' then
    if condition.value_type = 0 then
      ret := ret || 'not ' || prefix || 'tags @> ''' || quote_ident(condition.key) || '=>' || quote_ident(condition.value) || '''';
    else
      ret := ret || prefix || 'tags->' || quote_literal(condition.key) || ' != ' || final_value;
    end if;

  -- < > <= >=
  elsif condition.op in ('<', '>', '<=', '>=') then
    if condition.value_type = 0 then
      ret := ret || 'cast(' || prefix || 'tags->' || quote_literal(condition.key) || ' as numeric) ' || condition.op || ' ' || final_value;
    else
      ret := ret || 'pgmapcss_to_float(' || prefix || 'tags->' || quote_literal(condition.key) || ') ' || condition.op || ' pgmapcss_to_float(' || final_value || ')';
    end if;

  -- ^=
  elsif condition.op = '^=' then
    condition.value:=condition.value||'%';
    ret := ret || prefix || 'tags->' || quote_literal(condition.key) || ' similar to ' || final_value;

  -- $=
  elsif condition.op = '$=' then
    condition.value := '%' || condition.value;
    ret := ret || prefix || 'tags->' || quote_literal(condition.key) || ' similar to ' || final_value;

  -- *=
  elsif condition.op = '*=' then
    condition.value := '%' || condition.value || '%';
    ret := ret || prefix || 'tags->' || quote_literal(condition.key) || ' similar to ' || final_value;

  -- ~=
  elsif condition.op = '~=' then
    ret := ret || final_value || ' = any(string_to_array(' || prefix || 'tags->' || quote_literal(condition.key) || ', '';''))';

  -- =~
  elsif condition.op = '=~' then
    condition.op := '~';

    if condition.value ~ '^/(.*)/$' then
      m=substring(condition.value from '^/(.*)/$');
      if m is not null then
        condition.value=m;
        condition.op := '~';
      end if;

    elsif condition.value ~ '^/(.*)/i$' then
      m=substring(condition.value from '^/(.*)/i$');
      if m is not null then
        condition.value=m;
        condition.op := '~*';
      end if;
    end if;

    ret := ret || prefix || 'tags->' || quote_literal(condition.key) || ' ' || condition.op || ' ' || quote_literal(condition.value);

  -- unknown operator?
  else
    raise notice 'unknown condition operator: % (key: %, value: %)', condition.op, condition.key, condition.value;
    ret := 'true';

  end if;

  return ret;
end;
$$ language 'plpgsql' immutable;
