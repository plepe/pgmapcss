create or replace function eval_str(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
begin
  if array_upper(param, 1) is null then
    return '';
  end if;

  return param[1];
end;
$$ language 'plpgsql' immutable;

