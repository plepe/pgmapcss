from setuptools import setup, find_packages

setup(
    name = "pgmapcss",
    url = 'https://github.com/plepe/pgmapcss',
    author = 'Stephan Bösch-Plepelits',
    author_email = 'skunk' '@' 'xover.mud.at',
    description = 'PGMapCSS is a library for PostgreSQL/PostGIS which works between an osm2pgsql based database and Mapnik (and maybe other renderers). It processes database (usually OpenStreetMap) objects according to MapCSS rules and calculates resulting colors, widths and other properties for Symbolizers, even geometric modifications.',
    version = '0.5.0',
    packages = find_packages(),
    package_data = {
        'pgmapcss.db': [ '*.sql' ],
        'pgmapcss.db.eval': [ '*.sql' ],
        'pgmapcss.mapnik': [ '*.mapcss', '*.mapnik' ]
    },
    scripts = [ 'bin/pgmapcss' ],
)
