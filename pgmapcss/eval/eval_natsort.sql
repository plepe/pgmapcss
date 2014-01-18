create or replace function eval_natsort(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  list text[];
  i int;
begin
  if array_upper(param, 1) < 1 then
    return '';
  end if;

  list := string_to_array(param[1], ';');

  list := natcasesort(list);

  return array_to_string(list, ';');
end;
$$ language 'plpgsql' immutable;
