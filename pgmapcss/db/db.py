import postgresql
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
    files = [ 'pgmapcss_render_context.sql' ]

    for f in files:
        print('Installing', f)
        c = resource_string(__name__, f)
        c = c.decode('utf-8')
        conn.execute(c)

    db_version_update()

def db_init(conn):
    files = [ 'pgmapcss_types.sql' ]

    for f in files:
        print('Installing', f)
        c = resource_string(__name__, f)
        c = c.decode('utf-8')
        conn.execute(c)

    db_version_create()
    db_update(conn)

def install(style_id, style, conn):
    conn.execute(style['function_match'])

def prepare(sql):
    return conn.prepare(sql)

def query_functions():
    return resource_string(__name__, 'osm2pgsql.py').decode('utf-8')
