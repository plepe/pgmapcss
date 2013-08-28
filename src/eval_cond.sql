create or replace function eval_cond(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  ret text := '';
  i text;
  result boolean;
begin
  if array_upper(param, 1) >= 2 then
    result := eval_boolean(Array[param[1]], object, current, render_context);

    if result then
      return param[2];
    end if;

    if array_upper(param, 1) >= 3 then
      return param[3];
    end if;
  end if;

  return '';
end;
$$ language 'plpgsql' immutable;
