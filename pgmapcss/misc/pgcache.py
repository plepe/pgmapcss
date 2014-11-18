class PGCache:
    def __init__(self, id, read_id=False, read_geo=False):
        global PGCaches
        try:
            PGCaches
        except:
            PGCaches = {}

        PGCaches[id] = self

    def add(self, data, id=None, geo=None):
        pass

    def get(self, id=None):
        pass

    def query(self, qry):
        pass

def get_PGCache(id, read_id=False, read_geo=False):
    global PGCaches
    try:
        PGCaches
    except:
        PGCaches = {}

    return PGCaches[id]
