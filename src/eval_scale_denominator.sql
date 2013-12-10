create or replace function eval_scale_denominator(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
begin
  return render_context.scale_denominator;
end;
$$ language 'plpgsql' immutable;
