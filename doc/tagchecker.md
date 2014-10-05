This is a documentation of the tagchecker mode of pgmapcss. You should use pgmapcss in the 'standalone' mode, which will create an executable which - when run - will produce a GeoJSON file with all (possibily) erroneous objects.

```sh
pgmapcss --mode standalone -t tagchecker file.mapcss
```
will create a file `pgmapcss_file.py` which can be run from the commandline. It accepts the parameters `-b bounds` (e.g. `-b 16.3,48.1,16.4,48.2`) and `-s scale` (e.g. `-s 4000` or `-s z15`). see `pgmapcs_file.py --help` for details.

The following properties are available (similar to [JOSM TagChecker](https://josm.openstreetmap.de/wiki/Help/Validator/MapCSSTagChecker)). For compatibility with JOSM MapCSS TagChecker files, the "josm_classes" option will be enabled (`set foo;` implies `set .foo;`).

CSS parameter | Type | Description
--------------|------|---------------------------------------------------
throwError    | text | An error message
throwWarning  | text | A warning message
throwOther    | text | Other message
fixAdd        | list_append | To fix the above error/warning/other the following key/value combination should be added, e.g. "key=val".
fixRemove     | list_append | The tag key "key" should be removed.
fixChangeKey  | list_append | A tag key should be changed to another key, e.g. "old=>new".
suggestAlternative | list_append | An arbitrary message, suggesting changes.

* All statements with 'throwError', 'throwWarning' or 'throwOther' will produce a separate entry in the results array, see example below.
* Type 'list_append': If the property appears multiple times, it will be collected in a list (a string, separated by ';').

An example tagchecker mapcss file:
```css
way[highway][!ref] {
  throwOther: tr("highway without a reference");
  fixAdd: "ref";
  fixAdd: "int_ref";
}
way[highway=wrong] {
  throwError: tr("highway with wrong value");
}
```

An example GeoJSON output:
```json
{ "type": "FeatureCollection", "features": [
{
  "type": "Feature",
  "properties": {
    "osm:id": "w30323046",
    "highway": "wrong",
    "name": "Rotenturmstra\u00dfe",
    "results": [
      {
        "throwOther": "highway without a reference",
        "fixAdd": "ref;int_ref",
        "pseudo_element": "default",
      },
      {
        "throwError": "highway with wrong value",
        "pseudo_element": "default",
      }
    ],
  }
  "geometry": {
    "type": "LineString",
    "coordinates": [
      [
        16.374153861204505,
        48.210131336066524
      ],
      [
        16.374249441950738,
        48.21019838346531
      ],
      [
        16.374314659640365,
        48.21024405945546
      ],
    ]
  }
}
```
