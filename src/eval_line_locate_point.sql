create or replace function eval_line_locate_point(param text[],
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

  return eval_number(Array[
    ST_Line_Locate_Point(param[1], param[2]) * ST_Length(param[1])
    || 'u'], object, current, render_context);
end;
$$ language 'plpgsql' immutable;


