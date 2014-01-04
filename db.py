import postgresql
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
