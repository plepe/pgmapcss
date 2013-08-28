create or replace function eval_set(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  list text[];
  t text;
  i int;
begin
  if array_upper(param, 1) < 3 then
    return '';
  end if;

  t := eval_number(Array[param[2]], object, current, render_context);

  if t = '' then
    return '';
  end if;

  i := cast(t as int);

  if i < 0 then
    return '';
  end if;

  list := string_to_array(param[1], ';');

  list[i] := param[3];

  return array_to_string(list, ';', '');
end;
$$ language 'plpgsql' immutable;
