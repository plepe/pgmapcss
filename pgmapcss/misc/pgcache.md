PGCache implements a database cache with a postgis geometry column and the possibility to do queries into the database. PGCache comes in two flavours: *table*, where the data is written into a real postgresql database table or *virtual*, where the data is kept in memory and - if necessary - a virtual database table is used. Which flavour is used is decided by PGCache (usually *table*, only if the database happens to be read-only, *virtual* is used).

Example code:
```python
   try:
       cache = get_PGCache('foo')
   except:
       cache = PGCache('foo', read_id=True)
       cache.add({'id': '1', 'foo': 'bar' })
       cache.add({'id': '2', 'foo': 'foo' })
       cache.add({'id': '3', 'foo': 'bla' })

   for r in cache.get(['1', '2']):
       print(r)

   plan = cache.prepare('select * from {table}', [])
   for r in cache.cursor(plan):
       print(r)
```

The cache database table has the following columns:
* data: the data of the object in serialized form
* id: id of the object (see add() for details)
* geo: geometry of the object (see add() for details)

Functions Overview
==================
get_PGCache(): get an existing cache, will throw exception if it doesn't exist
------------------------------------------------------------------------------
Parameters:
* id: id of the cache
Return:
* return the existing cache

The following class functions are available:
constructor: initialize a new cache
----------------------------------
Parameters:
* id: identify cache
* read_id: (boolean) should the id of the object (if possible) should automatically be read (default False)
* read_geo: (boolean) should the geometry of the object (if possible) should automatically be read (default False)

add: add new data
-------------------
Parameters:
* data: some data, will be serialized (and on return unserialized)
* id: (optional, string) identify this object. If read_id is True and data a dict with a key 'id', this will be used
* geo: (optional, geometry) geometry of the object. If read_geo is True and data a dict with a key 'geo', this will be used

get(): a generator function returning data from cache
-----------------------------------------------------
Parameters:
* id: (optional, string or list of strings) only return data which matches the id.

prepare(): prepare a SQL select statement
-----------------------------------------
Parameters:
* query: (string) a database query containing "{table}" as database source, e.g. "select * from {table} where id=$1"
* param_type: (optional, list of type identifiers) parameter types to the database query, references by $1, $2, ... from the query, e.g. ['text']
Return:
* a plan, which can be passed to execute() or cursor()

execute(): execute a plan and return a list of result rows
----------------------------------------------------------
Parameters:
* plan: a plan from prepare()
* param: (optional, list) parameters to the database query, e.g. [ 'w1234' ]
Return:
* a list with all result rows. if 'data' is in the result columns it will be unserialized.

cursor(): execute a plan and yield result rows
----------------------------------------------
Parameters:
* plan: a plan from prepare()
* param: (optional, list) parameters to the database query, e.g. [ 'w1234' ]
Return:
* a generator generating result rows. if 'data' is in the result columns it will be unserialized.

