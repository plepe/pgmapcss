drop function if exists pgmapcss_compile_condition(pgmapcss_condition);
create or replace function pgmapcss_compile_condition(
  pgmapcss_condition
)
returns text
as $$
#variable_conflict use_variable
declare
  ret text := '';
  condition pgmapcss_condition;
  m text;
begin
  condition := $1;

  -- !
  if condition.op ~ '^!' then
    ret := ret || 'not ';
    condition.op := substring(condition.op, 2);
  end if;

  -- has_condition.key
  if condition.op = 'has_tag' then
    ret := ret || 'current.tags ? ' || quote_literal(condition.key);

  -- =
  elsif condition.op = '=' then
    ret := ret||'current.tags @> '''||quote_ident(condition.key)||'=>'||quote_ident(condition.value)||'''';

  -- !=
  elsif condition.op = '!=' then
    ret := ret||'not current.tags @> '''||quote_ident(condition.key)||'=>'||quote_ident(condition.value)||'''';

  -- < > <= >=
  elsif condition.op in ('<', '>', '<=', '>=') then
    ret := ret||'cast(current.tags->'||quote_literal(condition.key)||' as numeric) '||condition.op||' '||quote_literal(condition.value);

  -- ^=
  elsif condition.op = '^=' then
    condition.value:=condition.value||'%';
    ret := ret||'current.tags->'||quote_literal(condition.key)||' similar to '||quote_literal(condition.value);

  -- $=
  elsif condition.op = '$=' then
    condition.value:='%'||condition.value;
    ret := ret||'current.tags->'||quote_literal(condition.key)||' similar to '||quote_literal(condition.value);

  -- *=
  elsif condition.op = '*=' then
    condition.value:='%'||condition.value||'%';
    ret := ret||'current.tags->'||quote_literal(condition.key)||' similar to '||quote_literal(condition.value);

  -- ~=
  elsif condition.op = '~=' then
    ret := ret||quote_literal(condition.value)||'=any(string_to_array(current.tags->'||quote_literal(condition.key)||', '';''))';

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

    ret := ret||'current.tags->'||quote_literal(condition.key)||' '||condition.op||' '||quote_literal(condition.value);

  -- unknown operator?
  else
    raise notice 'unknown condition operator: % (key: %, value: %)', condition.op, condition.key, condition.value;
    ret := 'true';

  end if;

  return ret;
end;
$$ language 'plpgsql' immutable;
