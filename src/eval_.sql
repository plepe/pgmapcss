create or replace function eval_(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
begin
  return param[array_upper(param, 1)];
end;
$$ language 'plpgsql' immutable;
