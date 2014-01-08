import postgresql
from pkg_resources import *
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

    return conn

def init_db(conn):
    files = [ 'pgmapcss_types.sql', 'pgmapcss_object.sql', 'pgmapcss_render_context.sql', 'objects_osm2pgsql.sql', 'array_search.sql', 'natcasesort.sql', 'pgmapcss_to.sql' ]

    for f in files:
        print('Installing', f)
        c = resource_string(__name__, f)
        c = c.decode('utf-8')
        conn.execute(c)

    for f in resource_listdir(__name__, 'eval/'):
        if f[-4:] == '.sql':
            c = resource_string(__name__, 'eval/' + f)
            c = c.decode('utf-8')
            conn.execute(c)
            print('Installing', f)

def install(style_id, style, conn):
    conn.execute(style['function_check'])
    conn.execute(style['function_get_where'])
    conn.execute(style['function_match'])

def prepare(sql):
    return conn.prepare(sql)
