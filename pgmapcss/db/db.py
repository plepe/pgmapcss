import postgresql
import pgmapcss.data
from pkg_resources import *
from .version import *
import pgmapcss.db.osm2pgsql
import pgmapcss.db.osmosis
conn = None

def connection():
    return conn

def connect(args):
    global conn

    if not args.database_type in ('osm2pgsql', 'osmosis'):
        print('* Database type "{}" not supported right now'.format(args.database_type))
        exit(1)

    conn = postgresql.open(
        host=args.host,
        password=args.password,
        database=args.database,
        user=args.user
    )

    conn.database_type=args.database_type

    if args.database_type == 'osm2pgsql':
        conn.database = pgmapcss.db.osm2pgsql.db(conn)
    elif args.database_type == 'osmosis':
        conn.database = pgmapcss.db.osmosis.db(conn)
    else:
        raise Exception('unknown database type {}'.format(args.database_type))

    db_version_check()

    return conn

def db_update(conn):
    db_version_update()
    conn.database.update()

def db_init(conn):
    files = [ 'pgmapcss_types.sql', conn.database_type + '/init.sql' ]

    for f in files:
        print('Installing', f)
        c = resource_string(__name__, f)
        c = c.decode('utf-8')
        conn.execute(c)

    # populate _pgmapcss_left_right_hand_traffic table
    f = resource_stream(pgmapcss.data.__name__, 'left-right-hand-traffic.wkt')
    res = conn.prepare("insert into _pgmapcss_left_right_hand_traffic values (ST_Transform(ST_SetSRID($1::text, 4326), 900913))")
    while True:
        r = f.readline().decode('utf-8')
        if not r:
            break
        if r[0] != '#':
            res(r)
    f.close()

    db_version_create()
    db_update(conn)

    conn.database.init()

def install(style_id, style, conn):
    conn.execute(style['function_match'])

def prepare(sql):
    return conn.prepare(sql)

def query_functions():
    return resource_string(__name__, conn.database_type + '/db_functions.py').decode('utf-8')
