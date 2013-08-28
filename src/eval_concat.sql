create or replace function eval_concat(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret text := '';
  i text;
begin
  foreach i in array param loop
    ret := ret || i;
  end loop;

  return ret;
end;
$$ language 'plpgsql' immutable;
