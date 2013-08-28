insert into eval_operators values ('==', 'eq');
create or replace function eval_eq(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret float := 0;
  i int;
begin
  for i in 2..array_upper(param, 1) loop
    if param[1] != param[i] then
      return 'false';
    end if;
  end loop;

  return 'true';
end;
$$ language 'plpgsql' immutable;
