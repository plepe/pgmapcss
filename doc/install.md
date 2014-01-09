Installation on a plain Ubuntu 12.04.3 Server:

Install additional packages:
```sh
sudo apt-get install postgresql postgresql-contrib postgresql-9.1-postgis python-mapnik2 git osm2pgsql python3 python3-setuptools
```

More dependencies:
* pghstore
```sh
git clone https://github.com/plepe/pghstore.git
cd pghstore
sudo python3 setup.py install
```

Create database:
```sh
sudo su - postgres
createdb test
createuser -P user
exit
```
Initialize database:
```sh
psql -d "dbname=test user=user host=localhost password=PASSWORD" -c "create extension hstore"
psql -d "dbname=test user=user host=localhost password=PASSWORD" -f /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql
psql -d "dbname=test user=user host=localhost password=PASSWORD" -f /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql
```

Download an OSM file and import to database (you must add --hstore-all on newer osm2pgsql versions, as meaning of --hstore parameter changed):
```sh
osm2pgsql -dtest -Uuser -Hlocalhost -W -s -S /usr/share/osm2pgsql/default.style --hstore -G azores-latest.osm.bz2
```

Clone pgmapcss:
```sh
git clone https://github.com/plepe/pgmapcss.git
cd pgmapcss
```

Load pgmapcss functions, compile test.mapcss file. (If you use Mapnik 2.2 (or
higher) replace "-tmapnik20" by "-tmapnik22"):
```
./install.sh -dtest -uuser -pPASSWORD
./load.sh -dtest -uuser -pPASSWORD -tmapnik20 test.mapcss
```

You have a file test.mapnik which you can use in your preferred render front-end (e.g. renderd/mod_tile) OR generate an image with generate_image.py (if the Azores where not used as data, change "bounds" in file accordingly):
```sh
./generate_image.py
```
