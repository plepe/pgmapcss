create or replace function eval_locate_point(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  f float;
begin
  if array_upper(param, 1) < 2 then
    return '';
  end if;

  f := ST_Line_Locate_Point(param[1], param[2]);

  return ST_Line_Interpolate_Point(cast(param[1] as geometry), f);
end;
$$ language 'plpgsql' immutable;


