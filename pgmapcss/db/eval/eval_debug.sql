create or replace function eval_debug(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
begin
  if array_upper(param, 1) = 1 then
    raise notice '%', param[1];
  else
    raise notice '%', param;
  end if;

  return param[1];
end;
$$ language 'plpgsql' immutable;
