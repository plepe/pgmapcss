-- Create multicolumn way / tags indexes
do $$
begin
if not exists (
  select 1
  from pg_class
  where relname = 'planet_osm_point_way_tags'
  ) then

  raise notice E'\ncreating multicolumn indexes - please be patient ...';
  create index planet_osm_point_way_tags on planet_osm_point using gist(way, tags);
  create index planet_osm_line_way_tags on planet_osm_line using gist(way, tags);
  create index planet_osm_polygon_way_tags on planet_osm_polygon using gist(way, tags);
end if;
end$$;

-- Create index on planet_osm_rels members array
do $$
begin
if not exists (
  select 1
  from pg_class
  where relname = 'planet_osm_rels_members'
  ) then

  raise notice E'\ncreating planet_osm_rels members index - please be patient ...';
  create index planet_osm_rels_members on planet_osm_rels using gin(members);
end if;
end$$;

-- Create index on planet_osm_ways nodes array
do $$
begin
if not exists (
  select 1
  from pg_class
  where relname = 'planet_osm_ways_nodes'
  ) then

  raise notice E'\ncreating planet_osm_ways nodes index - please be patient ...';
  create index planet_osm_ways_nodes on planet_osm_ways using gin(nodes);
end if;
end$$;
