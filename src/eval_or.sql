insert into eval_operators values ('||', 'or', 1);
create or replace function eval_or(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  x text;
begin
  foreach x in array param loop
    if eval_boolean(Array[x], object, current, render_context) = 'true' then
      return 'true';
    end if;
  end loop;

  return 'false';
end;
$$ language 'plpgsql' immutable;

