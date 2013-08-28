insert into eval_operators values ('!=', 'neq');
insert into eval_operators values ('<>', 'neq');
create or replace function eval_neq(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret float := 0;
  i int;
begin
  select max(y) into i from (select count(x) y from (select unnest(param) x) t group by x) t;

  if i > 1 then
    return 'true';
  end if;

  return 'false';
end;
$$ language 'plpgsql' immutable;
