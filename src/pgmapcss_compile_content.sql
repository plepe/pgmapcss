create or replace function pgmapcss_compile_content (
  pgmapcss_compile_stat
)
returns pgmapcss_compile_stat
as $$
#variable_conflict use_variable
declare
  r record;
  r1 record;
  stat pgmapcss_compile_stat;
  prop_values_list text[];
  list text[];
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

  -- check final values (@values)
  -- replace possible property values by possible values
  for r in select * from each(stat.prop_values) loop
    prop_values_list := string_to_array(r.value, ';');
    list := Array[]::text[];

    for r1 in
      select
	(CASE
	  -- value NULL stays NULL
	  WHEN v is null THEN Array[NULL]::text[]
	  -- value '*' -> replaced by all possible values
	  WHEN v='*' THEN prop_values_list
	  -- 'correct' value -> remember
	  WHEN v = any(prop_values_list) THEN Array[v]
	  -- default value (first value)
	  ELSE Array[prop_values_list[1]]
	END) v
      from unnest(cast(stat.properties_values->(r.key) as text[])) v
    loop
      list := list || r1.v;
    end loop;

    stat.properties_values := stat.properties_values ||
      hstore(r.key, cast(array_unique(list) as text));
  end loop;


  return stat;
end;
$$ language 'plpgsql' immutable;
