from ..default import default
from ..pg import format
from ..pg import ident

class db(default):
    def __init__(self, conn, stat):
        default.__init__(self, conn, stat)

        if not 'db.srs' in self.stat['config']:
            if 'offline' in self.stat['options']:
                print('- Assuming SRS ID 900913. Specify -c db.srs=<value> if different')
                self.stat['config']['db.srs'] = 900913
            else:
                plan = self.conn.prepare('select ST_SRID(way) from planet_osm_point limit 1')
                res = plan()
                self.stat['config']['db.srs'] = res[0][0]
                print('- Database SRS ID {} detected'.format(self.stat['config']['db.srs']))

        # check database layout
        if 'db.hstore-only' in self.stat['config']:
            self.stat['config']['db.columns'] = False
            self.stat['config']['db.has-hstore'] = True

        elif 'db.columns' in self.stat['config']:
            self.stat['config']['db.columns'] = self.stat['config']['db.columns'].split(',')

        if not 'offline' in self.stat['options'] and not 'db.hstore-only' in self.stat['config']:
            plan = self.conn.prepare('select * from planet_osm_point limit 0')

            if not 'db.columns' in self.stat['config']:
                self.stat['config']['db.columns'] = [
                        k
                        for k in plan.column_names
                        if k not in ('osm_id', 'tags', 'way', 'z_order')
                    ]
                if len(self.stat['config']['db.columns']) == 0:
                    self.stat['config']['db.columns'] = False
                    self.stat['config']['db.hstore-only'] = True

            if not 'db.has-hstore' in self.stat['config']:
                self.stat['config']['db.has-hstore'] = 'tags' in plan.column_names

        self.stat['config']['sql.columns'] = ''
        if self.stat['config']['db.columns']:
            self.stat['config']['sql.columns'] = ',' + ', '.join([
                    '"' + k.replace('"', '_') + '"'
                    for k in self.stat['config']['db.columns']
                ])

    def tag_type(self, key):
        if key[0:4] == 'osm:':
            if key == 'osm:id':
                return ( 'column', 'osm_id', self.compile_modify_id )
            else:
                return None

        if self.stat['config']['db.columns']:
            if key in self.stat['config']['db.columns']:
                return ( 'column', key )

        if self.stat['config']['db.has-hstore']:
            return ( 'hstore-value', key, 'tags' )

        return None

    def compile_modify_id(self, key, value):
        if value[0] == 'r':
            return format(-int(value[1:]))
        else:
            return format(value[1:])
