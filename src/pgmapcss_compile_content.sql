create or replace function pgmapcss_compile_content (
  pgmapcss_compile_stat
)
returns pgmapcss_compile_stat
as $$
#variable_conflict use_variable
declare
  r record;
  stat pgmapcss_compile_stat;
begin
  stat := $1;
  stat.func :=''::text;
  stat.pseudo_elements := Array['default']::text[];
  stat.properties_values := ''::hstore;

  for r in select unnest(stat.selectors) selectors, unnest(stat.properties) properties loop
    stat := pgmapcss_compile_statement(r.selectors, r.properties, stat);
  end loop;

  -- copy possible values from @default_other to stat.properties_values
  for r in select * from each(stat.prop_default_other) loop
    stat.properties_values := stat.properties_values ||
      hstore(r.key, cast(array_unique(
        cast(stat.properties_values->(r.key) as text[]) ||
	cast(stat.properties_values->(r.value) as text[])
      ) as text));
  end loop;

  return stat;
end;
$$ language 'plpgsql' immutable;
