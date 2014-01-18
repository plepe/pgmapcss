create or replace function eval_search(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  list text[];
  i int;
begin
  if array_upper(param, 1) < 2 then
    return '';
  end if;

  list := string_to_array(param[1], ';');

  select n into i from (select generate_series(1, array_upper(list, 1)) n, unnest(list) x) t where x=param[2];

  if i is null then
    return 'false';
  end if;

  return i - 1;
end;
$$ language 'plpgsql' immutable;
