create or replace function eval_get(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  list text[];
  t text;
  i int;
begin
  if array_upper(param, 1) < 2 then
    return '';
  end if;

  t := eval_metric(Array[param[2]], object, current, render_context);

  if t = '' then
    return '';
  end if;

  i := cast(t as int);

  list := string_to_array(param[1], ';');

  if array_upper(list, 1) < i + 1 or i < 0 then
    return '';
  end if;

  return list[i + 1];
end;
$$ language 'plpgsql' immutable;
