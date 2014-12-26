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
                self.stat['config']['db.multipolygons-v0.2'] = not 'hide_outer_ways' in plan.column_names
            except postgresql.exceptions.UndefinedTableError:
                self.stat['config']['db.multipolygons'] = False

        if not 'db.srs' in self.stat['config']:
            if stat['config'].get('offline', False):
                print('- Assuming SRS ID 4326. Specify -c db.srs=<value> if different')
                self.stat['config']['db.srs'] = 4326
            else:
                plan = self.conn.prepare('select ST_SRID(geom) from nodes limit 1')
                res = plan()
                self.stat['config']['db.srs'] = res[0][0]
                print('- Database SRS ID {} detected'.format(self.stat['config']['db.srs']))

        if 'db.hstore_key_index' in stat['config']:
            stat['config']['db.hstore_key_index'] = stat['config']['db.hstore_key_index'].split(',')

    def tag_type(self, key, condition, selector, statement):
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
        if stat['config'].get('offline', False):
            print("Warning compiling tag 'osm:user': Can't optimize query, as user-ids can't be resolved at compile time.")
            return None

        plan = self.conn.prepare('select * from users where name=$1')
        res = plan(value)

        if(len(res)):
            return str(res[0][0])

        print("Warning compiling tag 'osm:user': User '{1}' not found.".format(key, value))
        return False
