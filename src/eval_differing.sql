insert into eval_operators values ('!=', 'differing', 5);
insert into eval_operators values ('<>', 'differing', 5);
create or replace function eval_differing(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  i int;
  values text[];
begin
  -- empty parameter list -> all equal
  if array_upper(param, 1) is null then
    return 'false';
  end if;

  -- identical comparison
  select count(v) into i from (select unnest(param) v group by v) t;

  if i != array_upper(param, 1) then
    return 'false';
  end if;

  -- convert all values to numbers
  select array_agg(v) into values from (
    select v from (
      select eval_metric(Array[v], object, current, render_context) v from
	(select unnest(param) v) t
    ) t group by v
  ) t;

  if array_upper(values, 1) != array_upper(param, 1) and not ('' = any(values)) then
    return 'false';
  end if;

  return 'true';
end;
$$ language 'plpgsql' immutable;
