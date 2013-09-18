create or replace function eval_sqrt(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret text := '';
  t text;
begin
  if array_upper(param, 1) >= 1 then
    if param[1] = '' or param[1] is null then
      t := '0';
    else
      t := eval_metric(Array[param[1]], object, current, render_context);

      if t = '' then
	return '';
      end if;
    end if;

    return cast(sqrt(cast(t as float)) as text);
  end if;

  return '';
end;
$$ language 'plpgsql' immutable;
