from ..default import default

class db(default):
    def tag_type(self, key):
        if key[0:4] == 'osm:':
            if key == 'osm:id':
                return ( 'all' )
            elif key == 'osm:user':
                return ( 'all' )
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
