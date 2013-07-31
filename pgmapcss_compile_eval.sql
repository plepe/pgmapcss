drop function pgmapcss_compile_eval(text);
create or replace function pgmapcss_compile_eval(
  text
)
returns text
as $$
#variable_conflict use_variable
declare
  ret text;
  param text[];
  eval_param text := ', id, tags, way, type, scale_denominator, current_style';
  p text[];
  t text;
  f text;
  i int;
begin
  if substr($1, 1, 2) = 'v:' then
    return quote_literal(substr($1, 3));
  end if;

  param := cast($1 as text[]);
  p := Array[]::text[];

  if param[1] !~ '^[fo]:' then
    return pgmapcss_compile_eval(param[1]);
  end if;

  for i in 2..array_upper(param, 1) loop
    p := array_append(p, pgmapcss_compile_eval(param[i]));
  end loop;

  t := 'Array[' || array_to_string(p, ', ') || ']::text[]';

  if    param[1] = 'o:+' then
    f:='add';
  elsif param[1] = 'o:-' then
    f:='sub';
  elsif param[1] = 'o:*' then
    f:='mul';
  elsif param[1] = 'o:/' then
    f:='div';
  elsif param[1] = 'o:>' then
    f:='gt';
  elsif param[1] = 'o:>=' then
    f:='ge';
  elsif param[1] = 'o:<=' then
    f:='le';
  elsif param[1] = 'o:<' then
    f:='lt';
  elsif param[1] = 'o:,' then
    f:='all';
  elsif substr(param[1], 1, 2) = 'f:' then
    f:=trim(substr(param[1], 3));
  end if;

  return 'eval_' || f || '(' || t || eval_param || ')';

  return '';
end;
$$ language 'plpgsql' immutable;
