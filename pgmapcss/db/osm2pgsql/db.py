from ..default import default
from ..pg import format
from ..pg import ident

class db(default):
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
