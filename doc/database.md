pgmapcss supports different kind of database layouts, currently osm2pgsql and osmosis pgsnapshot. Here's a short description of advantages and disadvantages.

osm2pgsql
=========
* Only nodes, ways and relations which are considered tagged by osm2pgsql can be used - as only those are added to the database tables. You can influence this list by change the osm2pgsql style file.
* Objects matching 'line' depend on the osm2pgsql style file; also relation=route are included in 'line'
* Objects matching 'area' depend on the osm2pgsql style file; also multipolygons and boundaries are included in 'area'.
* Generally no geometry or bounding box for relations, except for type=route, type=boundary, type=multipolygon. Queries for relations will return only those relations. On the other hand the 'type' tag is removed by osm2pgsql, therefore a query for `relation[type=route]` will not work.

osmosis pgsnapshot (short: osmosis)
===================================
* The osmosis database contains all nodes, ways and relations from OpenStreetMap. Especially the nodes table is very large and therefore queries for large bounding boxes may take a long time.
* 'line' and 'area' are synonymous to 'way'
* No multipolygon support.
* No geometry or bounding box for relations, queries for relation will return all available relations in the database.
