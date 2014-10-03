-- Create multicolumn way / tags indexes
do $$
begin
if not exists (
  select 1
  from pg_class
  where relname = 'nodes'
  ) then

  raise notice E'\ncreating multicolumn indexes - please be patient ...';
  create index nodes_geom_tags on nodes using gist(geom, tags);
  create index ways_linestring_tags on ways using gist(linestring, tags);
end if;
end$$;
