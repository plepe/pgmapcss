create or replace function eval_area(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  zoom	float;
begin
  if array_upper(param, 1) < 1 then
    return '';
  end if;

  zoom := eval_metric(Array['1u'], object, current, render_context);

  return ST_Area(param[1]) * zoom ^ 2;
end;
$$ language 'plpgsql' immutable;
