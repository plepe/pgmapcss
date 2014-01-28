create or replace function eval_not(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
begin
  if eval_boolean(param, object, current, render_context) = 'true' then
    return 'false';
  end if;

  return 'true';
end;
$$ language 'plpgsql' immutable;

