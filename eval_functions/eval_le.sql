insert into eval_operators values ('<=', 'le', 7);
create or replace function eval_le(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret text := '';
  i text;
  p1 float;
  p2 float;
begin
  if array_upper(param, 1) >= 2 then
    p1 := cast(eval_metric(Array[param[1]], object, current, render_context) as float);
    p2 := cast(eval_metric(Array[param[2]], object, current, render_context) as float);
    if p1 <= p2 then
      return 'true';
    else
      return 'false';
    end if;
  end if;

  return '';
end;
$$ language 'plpgsql' immutable;
