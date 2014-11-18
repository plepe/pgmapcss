class PGCache:
    def __init__(self, id, read_id=False, read_geo=False):
        global PGCaches
        try:
            PGCaches
        except:
            PGCaches = {}

        PGCaches[id] = self
        self.id = id
        self.read_id = read_id
        self.read_geo = read_geo
        self.cache_id = len(PGCaches)

    def add(self, data, id=None, geo=None):
        import pickle
        try:
            self.plan_add
        except:
            self.plan_add = plpy.prepare('insert into _pgmapcss_PGCache values (\'' + str(self.cache_id).replace("'", "''") + '\', $1, $2, $3)', [ 'bytea', 'text', 'geometry' ])

        if id is None and self.read_id and 'id' in data:
            id = data['id']
        if geo is None and self.read_geo and 'geo' in data:
            geo = data['geo']

        plpy.execute(self.plan_add, [ pickle.dumps(data), id, geo ])

    def get(self, id=None):
        import pickle
        if id is None:
            try:
                self.plan_get
            except:
                self.plan_get = plpy.prepare('select * from _pgmapcss_PGCache where cache_id=' + str(self.cache_id).replace("'", "''"), [])

            cursor = plpy.cursor(self.plan_get, [])

        else:
            try:
                self.plan_get_id
            except:
                self.plan_get_id = plpy.prepare('select * from _pgmapcss_PGCache where id=ANY($1) and cache_id=' + str(self.cache_id).replace("'", "''"), ['text[]'])

            if type(id) == str:
                id = [ id ]

            cursor = plpy.cursor(self.plan_get_id, [id])

        for r in cursor:
            yield pickle.loads(r['data'])

    def prepare(self, query, param_type=[]):
        return plpy.prepare(query.replace('{table}', '(select data, id, geo from _pgmapcss_PGCache where cache_id=' + str(self.cache_id).replace("'", "''") + ') t'), param_type)

    def execute(self, plan, param=[]):
        import pickle
        ret = []

        for r in plpy.execute(plan, param):
            if 'data' in r:
                r['data'] = pickle.loads(r['data'])
            ret.append(r)

        return ret

    def cursor(self, plan, param=[]):
        import pickle
        ret = []

        for r in plpy.cursor(plan, param):
            if 'data' in r:
                r['data'] = pickle.loads(r['data'])
            yield r

def get_PGCache(id, read_id=False, read_geo=False):
    global PGCaches
    try:
        PGCaches
    except:
        PGCaches = {}

    return PGCaches[id]
