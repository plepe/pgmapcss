create or replace function eval_rotate(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  x float;
  y float;
begin
  if array_upper(param, 1) is null then
    return '';
  elsif array_upper(param, 1) < 3 then
    param[3] := ST_Centroid(param[1]);
  end if;

  return 
    ST_Translate(
      ST_Rotate(
	ST_Translate(param[1], -X(param[3]), -Y(param[3])),
	radians(pgmapcss_to_float(param[2], 0))
      ),
      X(param[3]), Y(param[3])
    );
end;
$$ language 'plpgsql' immutable;



