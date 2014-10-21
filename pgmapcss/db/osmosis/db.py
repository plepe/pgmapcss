from pkg_resources import *
import postgresql
from ..default import default
from ..pg import format
from ..pg import ident

class db(default):
    def __init__(self, conn, stat):
        default.__init__(self, conn, stat)

        if not 'db.multipolygons' in self.stat['config']:
            try:
                plan = self.conn.prepare('select * from multipolygons limit 0')
                res = plan()
                print("- DB table 'multipolygons' detected; enabling support")
                self.stat['config']['db.multipolygons'] = True
            except postgresql.exceptions.UndefinedTableError:
                self.stat['config']['db.multipolygons'] = False

    def tag_type(self, key):
        if key[0:4] == 'osm:':
            if key == 'osm:id':
                return ( 'column', 'id', self.compile_modify_id )
            elif key == 'osm:user':
                return ( 'column', 'user_id', self.compile_user_id )
            elif key == 'osm:user_id':
                return ( 'column', 'user_id' )
            elif key == 'osm:version':
                return ( 'column', 'version' )
            elif key == 'osm:timestamp':
                return ( 'column', 'tstamp' )
            elif key == 'osm:changeset':
                return ( 'column', 'changeset_id' )
            else:
                return None

        return ( 'hstore-value', key, 'tags' )

    def compile_modify_id(self, key, value):
        return format(value[1:])

    def compile_user_id(self, key, value):
        plan = self.conn.prepare('select * from users where name=$1')
        res = plan(value)

        if(len(res)):
            return str(res[0][0])

        print("Warning compiling tag 'osm:user': User '{1}' not found.".format(key, value))
        return False
