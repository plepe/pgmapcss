create or replace function eval_debug(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
begin
  raise notice '%', param[1];

  return param[1];
end;
$$ language 'plpgsql' immutable;
