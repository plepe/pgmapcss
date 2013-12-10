create or replace function eval_zoom(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
begin
  return ceil(log(2, cast(3.93216e+08 / render_context.scale_denominator as numeric)));
end;
$$ language 'plpgsql' immutable;
