create or replace function eval_min(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  r text;
  f float;
  min float;
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

      if min is null or f < min then
	min := f;
      end if;
    end if;
  end loop;

  return coalesce(cast(min as text), '');
end;
$$ language 'plpgsql' immutable;
