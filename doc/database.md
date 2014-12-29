pgmapcss supports different kind of database layouts, currently osm2pgsql, osmosis pgsnapshot and overpass. Here's a short description of advantages and disadvantages.

osm2pgsql
=========
* Only nodes, ways and relations which are considered tagged by osm2pgsql can be used - as only those are added to the database tables. You can influence this list by change the osm2pgsql style file.
* Objects matching 'line' depend on the osm2pgsql style file; also relation=route are included in 'line'
* Objects matching 'area' depend on the osm2pgsql style file; also multipolygons and boundaries are included in 'area'.
* As direct query, only relations of type=route, type=boundary and type=multipolygon are available. On the other hand the 'type' tag is removed by osm2pgsql, therefore a query for `relation[type=route]` will not work.
* Queries of the type `relation node|way|relation` do work for all relation types as parents; even the type-tag is available. Currently those queries are inefficient, as for every possible member all available relations are queried.
* Queries of the type `way node` work. Currently those queries are inefficient, as for every possible member all available relations are queried.
* Additionally the tag "osm:id" will be set (e.g. 'n1234'), but it will not be available for querying (see below at osmosis pgsnapshot for additional tags).
* The osm2pgsql mode will by default use the tag columns of the database tables, and for other tags the "tags" column (type hstore), if available.

Options
-------
Behaviour can be influenced with the following config options:

| Config option    | Description | Possible values
|------------------|-------------|-----------------
| db.srs           | Spatial Reference System used in the database. Autodetected. | Usual values: 4326 (WGS-84), 900913 resp. 3857 (Spherical Mercator for Web Maps) |
| db.hstore-only   | Do not use the separate tag columns, only use the hstore 'tags' column. Might be faster on large databases in combination with a multicolumn index on way and tags: e.g. create index planet_osm_point_way_tags on planet_osm_point using gist(way, tags). Requires --hstore-all on osm2pgsql when importing the database. | true/**false** |
| db.columns.node  | Specify comma-separated list of database tag columns for planet_osm_point. Usually autodetected. Needed when using offline mode. | |
| db.columns.way   | Specify comma-separated list of database tag columns for planet_osm_line and planet_osm_polygon. Usually autodetected. Needed when using offline mode. | |
| db.columns       | Use the specified list for db.columns.node and db.columns.way | |
| db.has-hstore    | Additional tags can be read from the 'tags' column (of type hstore). Usually autodetected. Needed when using offline mode. | |

osmosis pgsnapshot (short: osmosis)
===================================
* The osmosis database contains all nodes, ways and relations from OpenStreetMap. Especially the nodes table is very large and therefore queries for large bounding boxes may take a long time.
* 'line' is synonymous to 'way'
* All closed ways are considered 'area's and their geometry converted to polygons.
* No native multipolygon support (see below).
* No geometry or bounding box for relations, queries for relation will return all available relations in the database.
* Additionally the tags "osm:id", "osm:version", "osm:user_id", "osm:user", "osm:timestamp", "osm:changeset" will be set, but they cannot (yet) be used for conditions (like `node[osm:user=skunk]`). Alternatively you may use `node[eval(tag("osm:user")=="skunk")]`, but it will not be as efficient.

Multipolygon support
--------------------
There's a module [osmosis-multipolygon](https://github.com/plepe/osmosis-multipolygon) which enables multipolygon support for an osmosis pgsnapshot database. The existance of the `multipolygons` table will be auto-detected and can be overridden by passing `-c db.multipolygons=true|false` to pgmapcss.

There are two "types" of multipolygons, those that have their tags bound to the relation (the standard) and multipolygons which inherit their tags from their outer members (when the relation has no relevant tags and the outer members have exactly the same relevant tags).

* "Standard" multipolygons get their ID prefixed by 'r' (as they are relations).
* Multipolygons with tags from their outer members get their ID prefixed by 'm' (for multipolygon) and an additional tag 'osm:has_outer_tags' (set to 'yes'). On the other hand closed ways which are an outer member of a multipolygon relation do not count as 'area', whereas the multipolygon itself does not count as 'relation'.

With osmosis-multipolygon v0.2 also multipolygons will be checked where the relation and the outer ways have the same tags (save non-relevant tags).

Options
-------
Behaviour can be influenced with the following config options:

| Config option    | Description | Possible values
|------------------|-------------|-----------------
| db.srs           | Spatial Reference System used in the database. Autodetected. | Usual values: 4326 (WGS-84), 900913 resp. 3857 (Spherical Mercator for Web Maps) |
| db.multipolygons | Specify whether the multipolygons table is present and should be used. Usually autodected. Needed when using offline mode (default: false) | true/false
| db.multipolygons-v0.2 | osmosis-multipolygon compatibility with version 0.1 (before the hide_outer_ways column had been added). | true/false

Overpass API (short: overpass)
==============================
In contrast to osm2pgsql and osmosis, Overpass API is an external database which is queried by HTTP requests. Also, the query language is very different from SQL. Overpass API is faster then PostgreSQL/PostGIS on large viewports.

By default, the API on overpass-api.de will be used, therefore it is not necessary to import a local copy. For sure, if you want to render on a regular base the admins of overpass-api.de will be happy if you change to a local copy. Additionally, you still need a local PostgreSQL database, as it is used for connecting to Mapnik and accessing the PostGIS functions.

* In contrast to osm2pgsql/osmosis the geometries need to be constructed on the fly which causes some additional overhead; including full multipolygon support (see below)
* In Overpass API, bounding box queries do not include ways and relations which cross the bounding box without having a node inside the bounding box, with the exception of [areas](http://wiki.openstreetmap.org/wiki/Overpass_API/Areas). Therefore very large objects might be missing in the output.
* Additionally the tags "osm:id", "osm:version", "osm:user_id", "osm:user", "osm:timestamp", "osm:changeset" will be set from OpenStreetMap meta info. Filtering for meta information is currently not possible on Overpass API, therefore these filters will not be applied to queries (in short: a condition for forests of user abc will be compiled into a query of all forests in the current viewport regardless of the user).

Multipolygon support
--------------------
There are two "types" of multipolygons, those that have their tags bound to the relation (the standard) and multipolygons which inherit their tags from their outer members (when the relation has no relevant tags and the outer members have exactly the same relevant tags, or the relation and the outer members have the same relevant tags).

* "Standard" multipolygons get their ID prefixed by 'r' (as they are relations).
* Multipolygons with tags from their outer members get their ID prefixed by 'm' (for multipolygon) and an additional tag 'osm:has_outer_tags' (set to 'yes'). On the other hand closed ways which are an outer member of a multipolygon relation do not count as 'area', whereas the multipolygon itself does not count as 'relation'.
* When the the relation and the outer members have the same relevant tags, the feature is handled as in the "standard" multipolygon way, but the outer ways do not match 'area'.

Options
-------
Behaviour can be influenced with the following config options:

| Config option    | Description | Possible values
|------------------|-------------|-----------------
| db.overpass-url  | overpass only: Use this alternative Overpass API url. default: http://overpass-api.de/api | |
| debug.overpass_queries | overpass only: Print a debug message for each query posted to the Overpass API | true/**false** |

Example usage:
```sh
pgmapcss --database-type=overpass -c db.overpass-url=http://overpass.osm.rambler.ru/cgi -d LOCAL_DB -u USER -p PASSWORD test.mapcss
```

* -d, -u and -p are the parameters of your local PostgreSQL database
