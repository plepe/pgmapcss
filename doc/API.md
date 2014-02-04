## {style_id}_match
Returns all matching objects and resulting properties in the current render context. Pseudo elements will add additional rows in the output. Every row will be returned multiple times, for each element in the style-element array. The result will be ordered by 'index of style-element', 'z-index' (asc, default 0).

Example:
```sql
select * from test_match(!bbox!, !scale_denominator!, Array['fill', 'line', 'text']);
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
