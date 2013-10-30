create or replace function eval_switch(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  p int;
  value text;
begin
  if array_upper(param, 1) is null then
    return '';
  end if;

  value := param[1];

  for p in 2..array_upper(param, 1) by 2 loop
    if value = any(string_to_array(param[p], ';')) then
      return param[p + 1];
    end if;
  end loop;

  if array_upper(param, 1) % 2 = 0 then
    return param[array_upper(param, 1)];
  end if;

  return '';
end;
$$ language 'plpgsql' immutable;

