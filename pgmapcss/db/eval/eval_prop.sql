create or replace function eval_prop(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  i int;
begin
  if array_upper(param, 1) = 0 then
    return '';
  end if;

  if array_upper(param, 1) >= 2 then
    i := array_search(param[2], current.pseudo_elements);

    if i is null then
      return '';
    end if;

  else
    i := current.pseudo_element_ind;

  end if;

  return current.styles[i]->param[1];
end;
$$ language 'plpgsql' immutable;
