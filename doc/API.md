# Using PGMapCSS
The postgresql function `pgmapcss_install(style_id, file_content)` converts the passed css file to some functions and a data type, as described in this page.

## Function {style_id}_check
Checks whether a single object matches any of the selectors in the CSS style at the current zoom level and returns the resulting properties. May return 0..n rows (a row per pseudo element), ordered by 'object-z-index' (asc, default 0).

Example usage (for style_id 'test'):
```sql
select * from test_check(object, render_context);
```

where object is of type `pgmapcss_object`:

| Column | Type     | Description |
| ------ | -------- | ----------- |
| id     | text     | the id of the object (recommended: N1234 for nodes, W1234 for ways, R1234 for relations) |
| tags   | hstore   | the tags of the object (e.g. '"highway"=>"primary", "name"=>"main Road"') |
| way    | geometry | the geometry of the object |
| types  | text[]   | object types that match this object, e.g. Array['way', 'area'] |

You may use the function `pgmapcss_object(id, tags, way, types)` to create an object for `test_check`.

The `render_context` can be derived with the function `pgmapcss_render_context(bbox, scale_denominator)`.

Full example usage (though, you better use {style_id}_match() instead):
```sql
select (result).* from (
  select test_check(
    pgmapcss_object('N'||osm_id, tags, way, Array['way', 'line']),
    pgmapcss_render_context(!bbox!, !scale_denominator!)
  ) result from planet_osm_point where way && !bbox! offset 0
) t
```

Notes:
* `!bbox!` and `!scale_denominator!` will be replaced by Mapnik by the current bounding box resp. scale denominator. See [zoom-to-scale.txt](https://trac.openstreetmap.org/browser/subversion/applications/rendering/mapnik/zoom-to-scale.txt) for valid values.
* `where way && !bbox!`: as the geometry may be modified by PGMapCSS, PostgreSQL can't use indexes on the resulting column; therefore all objects in the database would be included on every request (expect very bad performance). Using this statement PostgreSQL can use indexes on the source geometry and only objects matching the bounding box will be included.
* `offset 0`: the statement `(result).*` in the select statement will call `test_check()` for every resulting column; `offset 0` prevents this behaviour.

Example output:

| _style | _pseudo_element | _tags | _way | color | width | z-index | object-z-index |
| --- | --- | --- | --- | --- | --- | --- | --- |
| "color"=>"#A0A0A0", "width"=>"7", "z-index"=>"-20", "object-z-index"=>"-1" | casing | "name"=>"Testroad", "highway"=>"primary" | some geometry | #A0A0A0 | 7 | -20 | -1 |
| "color"=>"#ff0000", "width"=>"4" | default | "name"=>"Testroad", "highway"=>"primary" | some geometry | #ff0000 | 4 | | |

## {style_id}_match
Returns all matching objects and resulting properties in the current render context. Pseudo elements will add additional rows in the output. Every row will be returned multiple times, for each element in the style-element array. The result will be ordered by 'index of style-element', 'z-index' (asc, default 0).

Example:
```sql
select * from test_match(pgmapcss_render_context(!bbox!, !scale_denominator!), Array['fill', 'line', 'text']);
```

Notes:
* `!bbox!` and `!scale_denominator!` will be replaced by Mapnik by the current bounding box resp. scale denominator. See [zoom-to-scale.txt](https://trac.openstreetmap.org/browser/subversion/applications/rendering/mapnik/zoom-to-scale.txt) for valid values.

pgmapcss optimizes database queries for each zoom level, so that only objects that might be displayed will be returned. A selector has to include one (or more) of the properties `text`, `width`, `fill-color` (TODO: make list configurable) to be included in the query.

An example:
```css
line|z10-[highway=primary] {
  width: 2;
  color: #ff0000;
}
line|z12-[highway=secondary] {
  width: 1.5;
  color: #ff7f00;
}
```

will generate a query like
```sql
select * from planet_osm_line where (
  (tags @> 'highway=>primary')
) and way && !bbox!;
```
in zoom level 10 and 11, but for zoom level 12 and higher:
```sql
select * from planet_osm_line where (
  (tags @> 'highway=>primary') or
  (tags @> 'highway=>secondary')
) and way && !bbox!;
```

It even reconstructs classes, like:
```css
line[highway=residential],
line[highway=unclassified] {
  set .minor_road;
}

line.minor_road|z14- {
  width: 1;
  color: #ffff00;
}
```

Generated SQL for zoom level 14 and higher (including the CSS rules from the previous example):
```sql
select * from planet_osm_line where (
  (tags @> 'highway=>primary') or
  (tags @> 'highway=>secondary') or
  (tags @> 'highway=>residential') or
  (tags @> 'highway=>unclassified')
) and way && !bbox!;
```
