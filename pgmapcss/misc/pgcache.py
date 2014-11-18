# Example code:
#    try:
#        cache = get_PGCache('foo')
#    except:
#        cache = PGCache('foo', read_id=True)
#        cache.add({{'id': '1', 'foo': 'bar' }})
#        cache.add({{'id': '2', 'foo': 'foo' }})
#        cache.add({{'id': '3', 'foo': 'bla' }})
#
#    for r in cache.get(['1', '2']):
#        print(r)
#
#    plan = cache.prepare('select * from {table}', [])
#    for r in cache.cursor(plan):
#        print(r)
#
# The cache database table has the following columns:
# * data: the data of the object in serialized form
# * id: id of the object (see add() for details)
# * geo: geometry of the object (see add() for details)

class PGCache:
### __init__(): initialize a new cache
# Parameters:
#   id:        identify cache
#   read_id:   (boolean) should the id of the object (if possible) should automatically be read (default False)
#   read_geo:  (boolean) should the geometry of the object (if possible) should automatically be read (default False)
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

### add(): add new data
# Parameters:
#   data: some data, will be serialized (and on return unserialized)
#   id: (optional, string) identify this object. If read_id is True and data a dict with a key 'id', this will be used
#   geo: (optional, geometry) geometry of the object. If read_geo is True and data a dict with a key 'geo', this will be used
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

### get(): a generator function returning data from cache
# Parameters:
#   id: (optional, string or list of strings) only return data which matches the id.
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

### prepare(): prepare a SQL select statement
# Parameters:
#   query: (string) a database query containing "{table}" as database source, e.g. "select * from {table} where id=$1"
#   param_type: (optional, list of type identifiers) parameter types to the database query, references by $1, $2, ... from the query, e.g. ['text']
# Return:
#   a plan, which can be passed to execute() or cursor()
    def prepare(self, query, param_type=[]):
        return plpy.prepare(query.replace('{table}', '(select data, id, geo from _pgmapcss_PGCache where cache_id=' + str(self.cache_id).replace("'", "''") + ') t'), param_type)

### execute(): execute a plan and return a list of result rows
# Parameters:
#   plan: a plan from prepare()
#   param: (optional, list) parameters to the database query, e.g. [ 'w1234' ]
# Return:
#   a list with all result rows. if 'data' is in the result columns it will be unserialized.
    def execute(self, plan, param=[]):
        import pickle
        ret = []

        for r in plpy.execute(plan, param):
            if 'data' in r:
                r['data'] = pickle.loads(r['data'])
            ret.append(r)

        return ret

### cursor(): execute a plan and yield result rows
# Parameters:
#   plan: a plan from prepare()
#   param: (optional, list) parameters to the database query, e.g. [ 'w1234' ]
# Return:
#   a generator generating result rows. if 'data' is in the result columns it will be unserialized.
    def cursor(self, plan, param=[]):
        import pickle
        ret = []

        for r in plpy.cursor(plan, param):
            if 'data' in r:
                r['data'] = pickle.loads(r['data'])
            yield r

### get_PGCache(): get an existing cache, will throw exception if it doesn't exist
# Parameters:
#   id: id of the cache
# Return:
#   return the existing cache
def get_PGCache(id):
    global PGCaches
    try:
        PGCaches
    except:
        PGCaches = {}

    return PGCaches[id]
