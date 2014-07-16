import postgresql
import pgmapcss.data
from pkg_resources import *
from .version import *
conn = None

def connection():
    return conn

def connect(args):
    global conn
    conn = postgresql.open(
        host=args.host,
        password=args.password,
        database=args.database,
        user=args.user
    )

    db_version_check()

    return conn

def db_update(conn):
    db_version_update()

def db_init(conn):
    files = [ 'pgmapcss_types.sql', 'osm2pgsql.sql' ]

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

def install(style_id, style, conn):
    conn.execute(style['function_match'])

def prepare(sql):
    return conn.prepare(sql)

def query_functions():
    return resource_string(__name__, 'osm2pgsql.py').decode('utf-8')
