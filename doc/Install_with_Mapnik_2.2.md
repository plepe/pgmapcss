Installation on a plain Ubuntu 14.04 Server:

Install additional packages:
```sh
sudo apt-get install git postgresql postgresql-contrib postgresql-9.3-postgis-2.1 python3-setuptools python3-dev python-mapnik postgresql-plpython3 python3-postgresql ttf-unifont python3-wand imagemagick
```

More dependencies:
* pghstore

```sh
git clone https://github.com/plepe/pghstore.git
cd pghstore
python3 setup.py build
sudo python3 setup.py install
```

Create database:
```sh
sudo su - postgres
createdb test
createuser -s -P user
exit
```
Initialize database:
```sh
psql -d "dbname=test user=user host=localhost password=PASSWORD" -c "create extension hstore"
psql -d "dbname=test user=user host=localhost password=PASSWORD" -c "create extension postgis"
psql -d "dbname=test user=user host=localhost password=PASSWORD" -c "create language plpython3u"
```

Fix Mapnik fonts:
```sh
sudo mkdir /usr/lib/mapnik/fonts
for i in /usr/share/fonts/truetype/dejavu/* ; do sudo ln -s $i /usr/lib/mapnik/fonts/ ; done
sudo ln -s /usr/share/fonts/truetype/unifont/unifont.ttf /usr/lib/mapnik/fonts/
```

For the next step you can decide, whether you want to use overpass (default), osm2pgsql or osmosis as database backend.

Case 'overpass': You can use one of the public Overpass APIs (default), or [install your own](http://wiki.openstreetmap.org/wiki/Overpass_API/install).

Case 'osm2pgsql': Download an OSM file and import to database:
```sh
sudo apt-get install osm2pgsql
osm2pgsql -dtest -Uuser -Hlocalhost -W -s -S /usr/share/osm2pgsql/default.style --hstore -G azores-latest.osm.bz2
```

Case 'osmosis': Download an OSM file and import to database:
```sh
sudo apt-get install osmosis
mkdir pgimport
osmosis --read-xml azores-latest.osm.bz2 --write-pgsql-dump
cd pgimport
psql -d "dbname=test user=user host=localhost password=PASSWORD" -f /usr/share/doc/osmosis/examples/pgsnapshot_schema_0.6.sql
psql -d "dbname=test user=user host=localhost password=PASSWORD" -f /usr/share/doc/osmosis/examples/pgsnapshot_schema_0.6_linestring.sql
psql -d "dbname=test user=user host=localhost password=PASSWORD" -f /usr/share/doc/osmosis/examples/pgsnapshot_load_0.6.sql
```

Clone pgmapcss:
```sh
git clone https://github.com/plepe/pgmapcss.git
cd pgmapcss
python3 setup.py build
sudo python3 setup.py install
```

Compile 'test.mapcss' file and install database functions:
```
pgmapcss --database-type=TYPE -dtest -uuser -pPASSWORD -tmapnik-2.2 test
```

Replace TYPE by 'overpass' (default), 'osm2pgsql' or 'osmosis'. See [config_options.md](./config_options.md) for advanced options.

You get a file `test.mapnik` which you can use with your preferred render front-end (these are just examples):
* [Render an image](https://github.com/plepe/mapnik-render-image)
* [Run as WMS (Web Map Service)](https://github.com/mapbox/landspeed.js)
* [Run as TMS (Tile Map Service) with Apache2 and mod_tile](https://github.com/openstreetmap/mod_tile)
* [View in GUI](https://github.com/mapnik/mapnik/wiki/MapnikViewer)
