from ..default import default
from ..pg import format
from ..pg import ident

class db(default):
    def tag_type(self, key):
        if key[0:4] == 'osm:':
            if key == 'osm:id':
                return ( 'column', 'id', self.compile_modify_id )
            elif key == 'osm:user':
                return None
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
