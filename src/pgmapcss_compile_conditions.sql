create or replace function pgmapcss_compile_conditions (
  conditions pgmapcss_condition[],
  prefix text default ''
)
returns text
as $$
#variable_conflict use_variable
declare
  ret text := '';
begin
  if array_upper(conditions, 1) is null then
    return 'true';
  else
    return array_to_string((select array_agg(x) from (select pgmapcss_compile_condition(unnest(conditions), prefix) x) t), ' and ');
  end if;
end;
$$ language 'plpgsql' immutable;
