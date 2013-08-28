create or replace function eval_list(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
begin
  return array_to_string(param, ';');
end;
$$ language 'plpgsql' immutable;
