create or replace function eval_line_part(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  f float;
  l float;
  pos0 float;
  pos1 float;
begin
  if array_upper(param, 1) is null or array_upper(param, 1) < 2 then
    return '';
  end if;

  l := ST_Length(param[1]);

  pos0 := cast(eval_metric(Array[param[2], 'u'], object, current, render_context) as float);
  if array_upper(param, 1) < 3 then
    pos1 := l;
  else
    pos1 := cast(eval_metric(Array[param[3], 'u'], object, current, render_context) as float);
  end if;

  -- check for negative values
  if pos0 < 0 then
    pos0 := l - pos0;
  end if;

  if pos1 < 0 then
    pos1 := l - pos1;
  end if;

  -- check for valid values
  if pos0 < 0 then
    pos0 := 0;
  elsif pos0 > l then
    pos0 := l;
  end if;

  if pos1 < 0 then
    pos1 := 0;
  elsif pos1 > l then
    pos1 := l;
  end if;

  if pos1 < pos0 then
    return null;
  end if;

  return ST_Line_Substring(param[1], pos0 / l, pos1 / l);
end;
$$ language 'plpgsql' immutable;
