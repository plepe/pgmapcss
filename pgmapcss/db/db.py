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
    files = [ 'pgmapcss_object.sql', 'pgmapcss_render_context.sql', 'objects_osm2pgsql.sql', 'array_search.sql', 'natcasesort.sql', 'pgmapcss_to.sql', 'array_unique.sql', 'hstore_merge.sql' ]

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
    conn.execute(style['function_check'])
    conn.execute(style['function_get_where'])
    conn.execute(style['function_match'])

def prepare(sql):
    return conn.prepare(sql)
