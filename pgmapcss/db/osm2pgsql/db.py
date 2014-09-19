from ..default import default

class db(default):
    def tag_type(self, key):
        if key[0:4] == 'osm:':
            if key == 'osm:id':
                return ( 'all' )
            else:
                return None

        return ( 'hstore-value', key, 'tags' )
