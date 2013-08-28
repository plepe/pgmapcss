create or replace function eval_link_tag(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  i text;
begin
  foreach i in array param loop
    if (current.link_object).tags ? i then
      return (current.link_object).tags->i;
    end if;
  end loop;

  return null;
end;
$$ language 'plpgsql' immutable;
