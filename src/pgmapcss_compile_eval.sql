drop function if exists pgmapcss_compile_eval(text);
create or replace function pgmapcss_compile_eval(
  text
)
returns text
as $$
#variable_conflict use_variable
declare
  ret text;
  param text[];
  eval_param text := ', object, current, render_context';
  p text[];
  t text;
  f text;
  i int;
begin
  if substr($1, 1, 2) = 'v:' then
    return quote_literal(substr($1, 3));

  elsif substr($1, 1, 2) = 'f:' then
    return 'eval_' || quote_ident(substr($1, 3)) || '(''{}''' || eval_param || ')';

  end if;

  param := cast($1 as text[]);
  p := Array[]::text[];

  if array_upper(param, 1) is null then
    return '';
  end if;

  if param[1] !~ '^[fo]:' then
    return pgmapcss_compile_eval(param[1]);
  end if;

  for i in 2..array_upper(param, 1) loop
    p := array_append(p, pgmapcss_compile_eval(param[i]));
  end loop;

  t := 'Array[' || array_to_string(p, ', ') || ']::text[]';

  f := substring(param[1] from '^o:(.*)$');
  if f is not null then
    select func into f from eval_operators where eval_operators.op = f;
  elsif substr(param[1], 1, 2) = 'f:' then
    f:=trim(substr(param[1], 3));
  end if;

  return 'eval_' || f || '(' || t || eval_param || ')';

  return '';
end;
$$ language 'plpgsql' immutable;
