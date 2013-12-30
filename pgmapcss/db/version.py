import pgmapcss.version
import pgmapcss.db
import postgresql
from pkg_resources import parse_version

db_version_table_layout = 1

def db_version():
    try:
        res = pgmapcss.db.prepare("select * from pgmapcss_version")
    except postgresql.exceptions.UndefinedTableError:
        return None

    v = res()

    return { col: v[0][i] for i, col in enumerate(res.column_names) }

def db_version_check():
    """compares the installed version to the current pgmapcss version. Returns one of the following values:

    None: not installed (yet)
    0: same version as installed
    -1: installed version newer as current pgmapcss version
    1: current pgmapcss version newer as installed version (db functions update recommended)
    2: current pgmapcss version uses a different table layout (db re-init necessary)
    """
    global db_version_table_layout

    v = db_version()

    if not v:
        return None

    if v['table_layout'] != db_version_table_layout:
        return 2

    if parse_version(v['version']) == parse_version(pgmapcss.version.VERSION):
        return 0

    if parse_version(v['version']) < parse_version(pgmapcss.version.VERSION):
        return 1

    if parse_version(v['version']) > parse_version(pgmapcss.version.VERSION):
        return -1

def db_version_create():
    global db_version_table_layout

    conn = pgmapcss.db.connection()
    conn.execute('drop table if exists pgmapcss_version; create table pgmapcss_version ( version text, table_layout int );')
    r = conn.prepare('insert into pgmapcss_version values ( $1, $2 );')
    r(pgmapcss.version.VERSION, db_version_table_layout)

def db_version_update():
    conn = pgmapcss.db.connection()
    r = conn.prepare('update pgmapcss_version set version=$1')
    r(pgmapcss.version.VERSION)
