create or replace function eval_count(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  list text[];
begin
  if array_upper(param, 1) < 1 then
    return '';
  end if;

  if param[1] = '' then
    return '0';
  end if;

  list := string_to_array(param[1], ';');

  return array_upper(list, 1);
end;
$$ language 'plpgsql' immutable;
