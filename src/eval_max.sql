create or replace function eval_max(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  r text;
  f float;
  max float;
  list text[];
begin
  if array_upper(param, 1) > 1 then
    list := param;
  else
    list := string_to_array(param[1], ';');
  end if;

  if list is null then
    return '';
  end if;

  foreach r in array list loop
    r := eval_metric(Array[r], object, current, render_context);

    if r is not null and r != '' then
      f := cast(r as float);

      if max is null or f > max then
	max := f;
      end if;
    end if;
  end loop;

  return coalesce(cast(max as text), '');
end;
$$ language 'plpgsql' immutable;
