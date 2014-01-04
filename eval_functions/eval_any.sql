create or replace function eval_any(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  r text;
begin
  foreach r in array param loop
    if r is not null and r != '' then
      return r;
    end if;
  end loop;

  return '';
end;
$$ language 'plpgsql' immutable;
