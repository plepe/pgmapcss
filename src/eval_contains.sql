insert into eval_operators values ('~=', 'contains', 5);
create or replace function eval_contains(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  list text[];
  i int;
begin
  if array_upper(param, 1) < 2 then
    return '';
  end if;

  list := string_to_array(param[1], ';');

  select count(*) into i from (select unnest(list) x) t where x=param[2];

  if i = 0 then
    return 'false';
  else
    return 'true';
  end if;
end;
$$ language 'plpgsql' immutable;
