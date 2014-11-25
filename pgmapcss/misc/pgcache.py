def get_PGCache(id):
    global PGCaches
    try:
        PGCaches
    except:
        PGCaches = {}

    return PGCaches[id]

def PGCache(id, read_id=False, read_geo=False):
    global PGCache_type
    try:
        PGCache_type
    except:
        try:
            plan = plpy.prepare('insert into _pgmapcss_PGCache values (null, null, null, null)', [])
            plpy.execute(plan)
            plan = plpy.prepare('delete from _pgmapcss_PGCache where cache_id is null', [])
            plpy.execute(plan)

            PGCache_type = 1
        except:
            PGCache_type = 2

    if PGCache_type == 1:
        return PGCache_table(id, read_id, read_geo)
    elif PGCache_type == 2:
        return PGCache_virtual(id, read_id, read_geo)

class PGCache_base:
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

    def add(self, data, id=None, geo=None):
        pass

    def get(self, id=None):
        pass

    def prepare(self, query, param_type=[]):
        pass

    def execute(self, plan, param=[]):
        pass

    def cursor(self, plan, param=[]):
        pass

class PGCache_table(PGCache_base):
    def __init__(self, id, read_id=False, read_geo=False):
        global PGCaches
        super().__init__(id, read_id, read_geo)
        self.cache_id = len(PGCaches)

    def add(self, data, id=None, geo=None):
        import pickle
        try:
            self.plan_add
        except:
            self.plan_add = plpy.prepare('insert into _pgmapcss_PGCache values (\'' + str(self.cache_id).replace("'", "''") + '\', $1, $2, $3)', [ 'bytea', 'text', 'geometry' ])

        if id is None and self.read_id and type(data) is dict and 'id' in data:
            id = data['id']
        if geo is None and self.read_geo and type(data) is dict and 'geo' in data:
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

class PGCache_virtual(PGCache_base):
    def __init__(self, id, read_id=False, read_geo=False):
        super().__init__(id, read_id, read_geo)
        self.cache = []
        self.db_param = None

    def add(self, data, id=None, geo=None):
        if id is None and self.read_id and type(data) is dict and 'id' in data:
            id = data['id']
        if geo is None and self.read_geo and type(data) is dict and 'geo' in data:
            geo = data['geo']

        self.cache.append(( data, id, geo, ))
        self.db_param = None

    def get(self, id=None):
        if id is None:
            for r in self.cache:
                yield r[0]

        else:
            if type(id) == str:
                id = [ id ]

            for r in self.cache:
                if r[1] in id:
                    yield r[0]

    def prepare(self, query, param_type=[]):
        l = len(param_type)
        return plpy.prepare(query.replace('{table}', '(select unnest(${}) as data, unnest(${}) as id, unnest(${}) as geo) t'.format(l+1, l+2, l+3)), param_type + [ 'int[]', 'text[]', 'geometry[]' ])

    def get_db_param(self):
        if self.db_param is None:
            self.db_param = [
                    list(range(0, len(self.cache))),
                    [ r[1] for r in self.cache ],
                    [ r[2] for r in self.cache ],
                ]

        return self.db_param

    def execute(self, plan, param=[]):
        param += self.get_db_param()

        ret = []
        for r in plpy.execute(plan, param):
            if 'data' in r:
                r['data'] = self.cache[r['data']][0]
            ret.append(r)

        return ret

    def cursor(self, plan, param=[]):
        param += self.get_db_param()

        for r in plpy.cursor(plan, param):
            if 'data' in r:
                r['data'] = self.cache[r['data']][0]
            yield(r)
