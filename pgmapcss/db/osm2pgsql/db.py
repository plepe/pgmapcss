from ..default import default
from ..pg import format
from ..pg import ident

class db(default):
    def __init__(self, conn, stat):
        default.__init__(self, conn, stat)

        if not 'db.srs' in self.stat['config']:
            if stat['config'].get('offline', False):
                print('- Assuming SRS ID 900913. Specify -c db.srs=<value> if different')
                self.stat['config']['db.srs'] = 900913
            else:
                plan = self.conn.prepare('select ST_SRID(way) from planet_osm_point limit 1')
                res = plan()
                self.stat['config']['db.srs'] = res[0][0]
                print('- Database SRS ID {} detected'.format(self.stat['config']['db.srs']))

    def tag_type(self, key):
        if key[0:4] == 'osm:':
            if key == 'osm:id':
                return ( 'column', 'osm_id', self.compile_modify_id )
            else:
                return None

        return ( 'hstore-value', key, 'tags' )

    def compile_modify_id(self, key, value):
        if value[0] == 'r':
            return format(-int(value[1:]))
        else:
            return format(value[1:])
