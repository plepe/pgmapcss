from ..postgresql_db import postgresql_db
from ..pg import format
from ..pg import ident

class db(postgresql_db):
    def __init__(self, conn, stat):
        postgresql_db.__init__(self, conn, stat)

        if not 'db.srs' in self.stat['config']:
            if stat['config'].get('offline', False):
                print('- Assuming SRS ID 900913. Specify -c db.srs=<value> if different')
                self.stat['config']['db.srs'] = 900913
            else:
                plan = self.conn.prepare('select ST_SRID(way) from planet_osm_point limit 1')
                res = plan()
                self.stat['config']['db.srs'] = res[0][0]
                print('- Database SRS ID {} detected'.format(self.stat['config']['db.srs']))

        # check database layout
        if 'db.hstore-only' in self.stat['config']:
            self.stat['config']['db.columns.node'] = False
            self.stat['config']['db.columns.way'] = False
            self.stat['config']['db.has-hstore'] = True

        elif 'db.columns' in self.stat['config']:
            self.stat['config']['db.columns.node'] = self.stat['config']['db.columns'].split(',')
            self.stat['config']['db.columns.way'] = self.stat['config']['db.columns'].split(',')

        if not self.stat['config'].get('offline', False) and not 'db.hstore-only' in self.stat['config']:
            # detect layout of planet_osm_point for nodes
            plan = self.conn.prepare('select * from planet_osm_point limit 0')
            if not 'db.columns.node' in self.stat['config']:
                self.stat['config']['db.columns.node'] = [
                        k
                        for k in plan.column_names
                        if k not in ('osm_id', 'tags', 'way', 'z_order')
                    ]
                if len(self.stat['config']['db.columns.node']) == 0:
                    self.stat['config']['db.columns.node'] = False
                    self.stat['config']['db.hstore-only'] = True

            # detect layout of planet_osm_line for ways
            plan = self.conn.prepare('select * from planet_osm_line limit 0')
            if not 'db.columns.way' in self.stat['config']:
                self.stat['config']['db.columns.way'] = [
                        k
                        for k in plan.column_names
                        if k not in ('osm_id', 'tags', 'way', 'z_order', 'way_area')
                    ]
                if len(self.stat['config']['db.columns.way']) == 0:
                    self.stat['config']['db.columns.way'] = False
                    self.stat['config']['db.hstore-only'] = True

            if not 'db.has-hstore' in self.stat['config']:
                self.stat['config']['db.has-hstore'] = 'tags' in plan.column_names

        for t in [ 'node', 'way']:
            self.stat['config']['sql.columns.' + t] = ''
            if self.stat['config']['db.columns.' + t]:
                self.stat['config']['sql.columns.' + t] = ',' + ', '.join([
                        '"' + k.replace('"', '_') + '"'
                        for k in self.stat['config']['db.columns.' + t]
                    ])

        if 'db.hstore_key_index' in stat['config']:
            stat['config']['db.hstore_key_index'] = stat['config']['db.hstore_key_index'].split(',')

    def tag_type(self, key, condition, selector):
        if key[0:4] == 'osm:':
            if key == 'osm:id':
                return ( 'column', 'osm_id', self.compile_modify_id )
            else:
                return None

        type = None
        if selector['type'] in ('node', 'point'):
            type = 'node'
        if selector['type'] in ('way', 'line', 'area'):
            type = 'way'

        # type=route, type=multipolygon is not set for relations
        # TODO: a relation can also be an area -> how to handle this?
        if selector['type'] in ('relation') and key in ('type'):
            return None

        if type and self.stat['config']['db.columns.' + type]:
            if key in self.stat['config']['db.columns.' + type]:
                return ( 'column', key )

        if self.stat['config']['db.has-hstore']:
            return ( 'hstore-value', key, 'tags' )

        return None

    def compile_modify_id(self, key, value):
        if value[0] == 'r':
            return format(-int(value[1:]))
        else:
            return format(value[1:])
