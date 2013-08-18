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

  for r in select unnest(stat.selectors) selectors, unnest(stat.properties) properties loop
    stat := pgmapcss_compile_statement(r.selectors, r.properties, stat);
  end loop;

  return stat;
end;
$$ language 'plpgsql' immutable;
