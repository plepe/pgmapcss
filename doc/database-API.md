This is a documentation how support for a database backend is implemented in pgmapcss. It basically consists of a directory under pgmapcss/db (e.g. pgmapcss/db/osm2pgsql for the osm2pgsql backend) with three files: __init__.py, db.py and db_functions.py .

pgmapcss/db/TEMPLATE/__init__.py
=========================
```python
from .db import db
```

pgmapcss/db/TEMPLATE/db.py
=========================
The template file looks like this:
```python
from ..default import default

# This class implements the database backend for the TEMPLATE database layout.
class db(default):
    # function to initialize the database backend
    def __init__(self, conn, stat):
        # sets self.conn (the database connection) and self.stat (contains
        # everything about the current compile process, including the parsed
        # MapCSS tree, config options, ...)
        default.__init__(self, conn, stat)

        # this function may check and set config options in
        # self.stat['config'], e.g. self.stat['config']['my_opt'] = True
        # this might come in handy later-on in db_functions.py

    # compile the conditions of the selector (e.g. `node[amenity=bar][name]`)
    # to a select condition without selecting the object type
    # (e.g. `"amenity"='bar' and "name" is not null` or
    # `tags @> 'amenity=>bar' and tags ? 'name'`).
    # see below for the structure of the selector argument
    # for good performance it would be advisable to also compile relationships
    # You may define the datatype of the return value, with the exception of
    # False -> the condition will be dropped
    def compile_selector(self, selector):
        pass

    # merge several compiled selectors together (the argument conditions is a
    # list)
    # e.g. `[ '"amenity"=\'bar\' and "name" is not null', '"foo"=\'bar\'' ]`
    # => `'("amenity"=\'bar\' and "name" is not null) or ("foo"=\'bar\')'`
    # You may define the datatype of the return value, with the exception of
    # False -> the conditions will be dropped
    def merge_conditions(self, conditions):
        pass
```

pgmapcss/db/TEMPLATE/db_functions.py
===================================
This file will be included in the compiled executable / database function. All the functions may return more objects as actually needed, the objects will be checked again later-on during processing (though this will reduce performace. you can set the config option `db.counter=verbose` to see which objects were returned but not rendered in the output).

An object should look like this:
```python
{
    'id': 'w1234',              # identifier
    'types': [ 'way', 'area' ], # types this object might match
    'geo': '01010000...',       # geometry in Well-Known Binary representation
    'tags': { 'foo': 'bar' },   # tags of the object
    'members': [                # (optional) list of members, with link tags
        { 'member_id': 'n234', 'sequence_id': '0' },
        { 'member_id': 'n235', 'sequence_id': '1' }
    ]
}
```

The template file looks like this:
```python
# objects_bbox() yields all objects which match the query/queries in the current
# bounding box.
#
# Arguments:
# bbox: a bounding box as WKT or None (ignore bounding box ; return all objects
#       in database)
# db_selects: a dict, with the object types and the compiled conditions from db.py, e.g.: `{ 'area': '("amenity"=\'bar\' and "name" is not null) or ("foo"=\'bar\')' }`. objects_bbox() need to match the object types to the respective openstreetmap objects, e.g. 'area' => closed ways and multipolygons.
# options: a dict, with additional settings (currently: none)
def objects_bbox(bbox, db_selects, options):
    pass

# objects_by_id() yields the specified objects from the database
# an id is a string with the object type identifier and the id, e.g. 'n1234'
# options: a dict, with additional settings (currently: none)
def objects_by_id(id_list, options):
    pass

# objects_member_of(). For each object in the `objects` list, return all parent
# objects (which match the db_selects).
#
# Arguments:
# objects: a list of objects
# other_selects: a query/queries how to select parent objects (see db_selects on objects_bbox())
# self_selects: a query/queries how to select child objects (this might be useful if you want to query all objects in the bounding box for caching)
# options: a dict, with additional settings (currently: none)
#
# Yields:
# As yielded values, tuples are expected with:
# ( child_object, parent_object, link_tags )
#
# link_tags (dict) should contain:
# * sequence_id: members are consecutively numbered, the child is the nth entry (counting from 0)
# * role: role as specified in osm data (when the parent is a relation)
def objects_member_of(objects, other_selects, self_selects, options):
    pass

# objects_members(). For each object in the `objects` list, return all child
# objects (which match the db_selects).
#
# Arguments:
# objects: a list of objects
# other_selects: a query/queries how to select child objects (this might be useful if you want to query all objects in the bounding box for caching)
# self_selects: a query/queries how to select parent objects (see db_selects on objects_bbox())
# options: a dict, with additional settings (currently: none)
#
# Yields:
## As yielded values, tuples are expected with:
# ( parent_object, child_object, link_tags )
# link_tags (dict) should contain:
# * sequence_id: members are consecutively numbered, the child is the nth entry (counting from 0)
# * role: role as specified in osm data (when the parent is a relation)
def objects_members(objects, other_selects, self_selects, options):
    pass

# objects_near(). For each object in the `objects` list, return all nearby objects (which match the db_selects).
#
# Arguments:
# objects: a list of objects
# other_selects: a query/queries how to select the other objects (see db_selects on objects_bbox())
# self_selects: a query/queries how to select the objects from which we query (this might be useful if you want to query all objects in the bounding box for caching)
# options: a dict, with additional settings:
# * distance: maximum distance in pixels
# * check_geo: (optional) one of:
#   * 'within': if child object is within certain distance around parent
#   * 'surrounds': if parent object is within certain distance around child
#   * 'overlaps': if parent object and child object overlap (distance=0)
#
# Yields:
# As yielded values, tuples are expected with:
# ( parent_object, child_object, link_tags )
# link_tags (dict) should contain:
# * distance: distance between objects in pixels
def objects_near(objects, other_selects, self_selects, options):
    pass
```

APPENDIX
========
Structure of parsed selector
----------------------------
An example selector structure looks like this:
```css
node[amenity=bar][name] {
    text: "name";
    text-color: #ff0000;
}
```

```python
{
    'type': 'node',          # selected type; True if any type (*)
    'conditions': [
        {
            'key': 'amenity',
            'op': '=',
            'value': 'bar',
            'value_type': 'value' # one of (value, eval)
        }, {
            'key': 'name',
            'op': 'has_tag'
        }
    ]
}
```

An example using relationships:
```css
relation[type=route] >[role=stop] node {
    text: parent_tag('ref');
}
```

```python
{
    'type': 'node',
    'conditions': [],        # no conditions on node
    'link': {                # (optional) when using relationship selector
        'type': '>'          # '', '>', '<', 'near', 'within', 'overlaps' or 'surrounds'
        'conditions': [
            {
                'key': 'role',
                'op': '=',
                'value': 'stop',
                'value_type': 'value'
            }
        ]
    },
    'parent': {              # (optional) when using relationship selector
        'type': 'relation'
        'conditions': [
            {
                'key': 'type',
                'op': '=',
                'value': 'route',
                'value_type': 'value'
            }
        ]
    }
}
```
