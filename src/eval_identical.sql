insert into eval_operators values ('===', 'identical', 5);
insert into eval_operators values ('eq', 'identical', 5);
create or replace function eval_identical(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  i int;
begin
  -- identical comparison
  select count(v) into i from (select unnest(param) v group by v) t;
  
  if i > 1 then
    return 'false';
  end if;

  return 'true';
end;
$$ language 'plpgsql' immutable;

