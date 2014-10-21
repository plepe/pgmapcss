## API



### Mode 'database-function': pgmapcss_{style_id}()
Returns all matching objects and resulting properties in the current render context. Pseudo elements will add additional rows in the output. Every row will be returned multiple times, for each element in the style-element array. The result will be ordered by 'index of style-element', 'z-index' (asc, default 0).

* Example:
```sql
select * from pgmapcss_test(!bbox!, !scale_denominator!, Array['fill', 'line', 'text']);
```

* Return:
This function will return a row for each feature and each pseudo element. The structure will contain the following columns:

Column name | Type | Description
------------|------|-------------
id          | text | The ID of the feature, e.g. 'n1234'.
tags        | hstore   | Key/Value of the (modified) tags of the feature.
geo         | geometry | The geometry of the object
types       | text[]   | Types for selectors the feature belongs too, e.g. Array['way', 'area'].
pseudo_element | text  | The pseudo element for which properties have been calculated, default 'default'.
properties  | hstore   | How the feature should be styled, with colors, widths, dashes, texts, ...
style_elements         | text[] | On which style elements the feature will be shown, e.g. casing, line, point-text, ...
style_elements_index   | int[]  | Index of all style elements in the all_style_elements array (from calling the function).
style_elements_layer   | float[] | Layer where each style element should be shown.
style_elements_z_index | float[] | z-index for each style element.

Notes:
* `!bbox!` and `!scale_denominator!` will be replaced by Mapnik by the current bounding box resp. scale denominator. See [zoom-to-scale.txt](https://trac.openstreetmap.org/browser/subversion/applications/rendering/mapnik/zoom-to-scale.txt) for valid values.

### Mode 'standalone': file pgmapcss_{style_id}.py
When compiling in 'standalone' mode, a file pgmapcss_{style_id}.py will be created, which can be used either from command line or as CGI script. In any case it will produce GeoJSON output. See below for details.

#### command line
```
usage: pgmapcss_{style_id}.py [-h] [-b BOUNDS] [-s SCALE]
                       [-P PARAMETERS [PARAMETERS ...]] [--lang LANG]

Executes the compiled map style and prints resulting objects.

optional arguments:
  -h, --help            show this help message and exit
  -d DATABASE, --database DATABASE
                        Name of database (default: as set at compile time)
  -u USER, --user USER  User for database (default: as set at compile time)
  -p PASSWORD, --password PASSWORD
                        Password for database (default: as set at compile
                        time)
  -H HOST, --host HOST  Host for database (default: as set at compile time)
  -b BOUNDS, --bounds BOUNDS
                        Process the map from the specified bounding box as
                        min_lon,min_lat,max_lon,max_lat in WGS-84. (default:
                        whole database)
  -s SCALE, --scale SCALE
                        Process map at a specified scale denominator. If
                        z<zoom> syntax (e.g. "z15") is used, the zoom levels
                        of projection 900913 are used.
  -P PARAMETERS [PARAMETERS ...], --parameters PARAMETERS [PARAMETERS ...]
                        Pass the following parameters as key-value pairs to
                        the MapCSS code, e.g. "-P foo=bar test='Hello World!'
  --lang LANG           Use the given language code (e.g. "en" or "de") for
                        language dependend instruction (e.g. function lang(),
                        text:auto, ...). Default: language from current locale
                        $LANG (or "en").
```

#### CGI script
Parameter key | Description
--------------|-------------
bbox          | Process the map from the specified bounding box as min_lon,min_lat,max_lon,max_lat in WGS-84. (default: whole database)
scale         | Process map at a specified scale denominator.
zoom          | zoom level of standard tile based map (projection 900913)
x, y          | x/y tiles as with images (jpg/png)
z             | zoom level in combination with x/y tiles. If a different tilesize (e.g. 512 or 1024) is used, the zoom level will be adapted automatically. With tilesize 256, zoom and z are equal.
tilesize      | the tilesize when using x/y tiles (default: 256)
lang          | Use the given language code (e.g. "en" or "de") for language dependend instructions. Default: the first value of the HTTP Accept-Language header.
srs           | ID of projection of output coordinates (default: 4326).
OTHER         | all other parameters will be available via the parameters() function.

#### GeoJSON output
Some example output (shortened). As you can see, the "results" part of "properties" may contain several items, for each pseudo element.
```json
{ "type": "FeatureCollection",
  "crs": { "type": "name", "properties": { "name": "EPSG:4326" } },
  "features": [
    {
      "geometry": {
        "coordinates": [
          [
            [
              16.337591800000002,
              48.1962632
            ],
            [
              16.33854560000001,
              48.19641519999998
            ],
            [
              16.338791000000004,
              48.19577849999998
            ],
            [
              16.338288700000007,
              48.195607599999995
            ],
            [
              16.337591800000002,
              48.1962632
            ]
          ]
        ],
        "type": "Polygon"
      },
      "type": "Feature",
      "properties": {
        "osm:version": "4",
        "osm:timestamp": "2012-12-11 12:23:36",
        "name": "Wolkenspange",
        "layer": "1",
        "osm:user": "FS161820",
        "osm:changeset": "14236986",
        "building": "yes",
        "results": [
          {
            "pseudo_element": "building",
            "layer": "1",
            "fill-color": "#b8b6a5",
            "fill-opacity": "1"
          }
        ],
        "osm:id": "w138332040",
        "osm:user_id": "102703"
      }
    },
    {
      "geometry": {
        "coordinates": [
          [
            16.337196200000005,
            48.19669469999999
          ],
          [
            16.336341799999996,
            48.19649939999998
          ],
          [
            16.332081300000002,
            48.195418800000006
          ]
        ],
        "type": "LineString"
      },
      "type": "Feature",
      "properties": {
        "gauge": "1435",
        "osm:version": "10",
        "osm:timestamp": "2014-05-23 18:15:05",
        "operator": "\u00d6BB",
        "voltage": "15000",
        "osm:user": "RolandS",
        "results": [
          {
            "width": "6",
            "opacity": "1",
            "dashes": "0,2,1,2",
            "pseudo_element": "rail_dash",
            "color": "#707070"
          },
          {
            "width": "2",
            "opacity": "1",
            "dashes": "none",
            "pseudo_element": "rail",
            "color": "#707070"
          }
        ],
        "electrified": "contact_line",
        "railway": "rail",
        "frequency": "16.7",
        "osm:changeset": "22508133",
        "osm:id": "w8037875",
        "tracks": "1",
        "osm:user_id": "137823",
        "railway:track_ref": "6"
      }
    }
  ]
}
```

## Internal stuff
### How a style is translated to database queries
pgmapcss optimizes database queries for each zoom level, so that only objects that might be displayed will be returned. A selector has to include one (or more) of the properties `text`, `width`, `fill-color` (configured via the `@style_element_property`) to be included in the query.

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
