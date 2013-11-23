create or replace function pgmapcss_compile_conditions (
  conditions pgmapcss_condition[],
  prefix text default '',
  match_where boolean default false
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
    return coalesce(array_to_string((select array_agg(x) from (select pgmapcss_compile_condition(unnest(conditions), prefix, match_where) x) t where x is not null), ' and '), 'false');
  end if;
end;
$$ language 'plpgsql' immutable;
