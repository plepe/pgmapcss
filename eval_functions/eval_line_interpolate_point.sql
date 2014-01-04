create or replace function eval_line_interpolate_point(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  f float;
  l float;
begin
  if array_upper(param, 1) < 1 then
    return '';
  end if;

  l := ST_Length(param[1]);

  if array_upper(param, 1) < 2 then
    f := 0.5;
  else
    f := pgmapcss_to_float(eval_metric(Array[param[2], 'u'], object, current, render_context)) / l;
  end if;

  -- check for valid values
  if f is null then
    return '';
  elsif f < 0 then
    f := 0;
  elsif f > 1 then
    f := 1;
  end if;

  return ST_Line_Interpolate_Point(param[1], f);
end;
$$ language 'plpgsql' immutable;


