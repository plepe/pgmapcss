# Using PGMapCSS
The postgresql function `pgmapcss_install(style_id, file_content)` converts the passed css file to some functions and a data type, as described in this page.

## Type {style_id}_result
A data type `{style_id}_result` will be created which returns some fixed columns and a column for each property.

Return values (Data Type '{style_id}_result'):
| Name   | Type     | Description        |
| ------ | -------- | ------------------ |
| _style | hstore   | All resulting properties |
| _pseudo_element | text | The current pseudo element, default: 'default'.
| _tags  | hstore   | The resulting tags, as modified by set and unset statements. |
| _geo   | geometry | (Modified) geometry |
| ...    | text     | A column for every property found in the CSS file. |

The `{style_id}_check` and `{style_id}_match` functions each return 0..n rows of type `{style_id}_result`.

## Function {style_id}_check
Checks whether an objects matches any of the selectors in the CSS style at the current zoom level. May return 0..n rows (a row per pseudo element), ordered by 'object-z-index' (asc, default 0).

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

Full example usage:
```sql
select (result).* from (
  select test_check(
    pgmapcss_object('N'||osm_id, tags, way, Array['way', 'line']),
    pgmapcss_render_context(!bbox!, !scale_denominator!)
  ) result from planet_osm_point where way && !bbox! offset 0
) t
```

Notes:
* `!bbox!` and `!scale_denominator!` will be replaced by Mapnik by the current bounding box resp. scale denominator. See [[https://trac.openstreetmap.org/browser/subversion/applications/rendering/mapnik/zoom-to-scale.txt|zoom-to-scale.txt]] for valid values.
* `where way && !bbox!`: as the geometry may be modified by PGMapCSS (though not implemented yet), PostgreSQL can't use indexes on the resulting column; therefore all objects in the database would be included on every request (expect very bad performance). Using this statement PostgreSQL can use indexes on the source geometry and only objects matching the bounding box will be included.
* `offset 0`: the statement `(result).*` in the select statement will call `test_check()` for every resulting column; `offset 0` prevents this behaviour.

Example output:
| _style | _pseudo_element | _tags | _way | color | width | z-index | object-z-index |
| --- | --- | --- | --- | --- | --- | --- | --- |
| "color"=>"#A0A0A0", "width"=>"7", "z-index"=>"-20", "object-z-index"=>"-1" | casing | "name"=>"Testroad", "highway"=>"primary" | some geometry | #A0A0A0 | 7 | -20 | -1 |
| "color"=>"#ff0000", "width"=>"4" | default | "name"=>"Testroad", "highway"=>"primary" | some geometry | #ff0000 | 4 | | |
