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
    t := eval_number(Array[param[1]], object, current, render_context);

    if t = '' then
      return '';
    end if;

    return cast(sqrt(cast(t as float)) as text);
  end if;

  return '';
end;
$$ language 'plpgsql' immutable;
