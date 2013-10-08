insert into eval_operators values ('!==', 'nonidentical', 5);
insert into eval_operators values ('ne', 'nonidentical', 5);
create or replace function eval_nonidentical(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  i int;
begin
  -- empty parameter list -> all equal
  if array_upper(param, 1) is null then
    return 'false';
  end if;

  -- identical comparison
  select count(v) into i from (select unnest(param) v group by v) t;
  
  if i != array_upper(param, 1) then
    return 'false';
  end if;

  return 'true';
end;
$$ language 'plpgsql' immutable;

