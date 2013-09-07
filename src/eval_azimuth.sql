create or replace function eval_azimuth(param text[],
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

  return degrees(ST_Azimuth(param[1], param[2]));
end;
$$ language 'plpgsql' immutable;



