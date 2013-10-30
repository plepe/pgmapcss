create or replace function eval_power(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
begin
  if array_upper(param, 1) is null or array_upper(param, 1) < 2 then
    return '';
  end if;

  return cast(eval_metric(Array[param[1]], object, current, render_context) as float) ^
         cast(eval_metric(Array[param[2]], object, current, render_context) as float);
end;
$$ language 'plpgsql' immutable;

