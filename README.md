pgmapcss
========
pgmapcss is [Mapnik](http://www.mapnik.org/) for [OpenStreetMap](http://www.openstreetmap.org/) on steroids :-) Writing Mapnik stylesheets is a tedious work, requiring you to write stylesheets in XML with complex database queries. Even when using pre-processors like [Cascadenik](https://github.com/mapnik/Cascadenik) or [CartoCSS](http://wiki.openstreetmap.org/wiki/Carto) you still need to have some knowledge in SQL.

MapCSS takes away all this pain. It's simple and declarative: You define what should be rendered how, using CSS-like language. MapCSS is very powerful as it allows calculations. MapCSS is a somehow standardized language as there are many different renderers supporting it (although each dialect is a little different).

pgmapcss compiles MapCSS styles into a database function. Mapnik just needs to call this database function and render the processed data.

Features
--------
### Writing MapCSS styles is simple, e.g.: ###
```css
line|z15-[highway=primary] {
  color: #ffff00;
  width: 6;
  casing-color: #303030;
  casing-width: 1.5;
  text: name;
  text-color: blue;
}
```

Every line with highway=primary should be displayed with a yellow 6px wide line with a 1.5px darkgrey casing (on both sides). Additional the value of the 'name'-tag should be shown on top of the line in the CSS3 color blue. This style is valid from zoom level 15 on.

See [MapCSS Documentation](doc/MapCSS.creole) for general documentation about pgmapcss' dialect of the MapCSS language and [the list of available properties (Mapnik 2.2)](doc/mapnik-2.2.creole) for possible style parameters (resp. [here for Mapnik 2.0](doc/mapnik-2.0.creole) and [here for the experimental "expr-v2" branch](doc/expr-v2.creole)).

### Extensive eval-syntax: ###

Using eval(), values for properties can be calculated. Even geometric modifications are possible as many PostGIS functions are exposed. Examples:
```css
line|z15-[highway=primary] {
  /* print "ref - name" as text, e.g. "B1 - Wienerstraße". */
  text: eval(tag("ref") . " - " . tag("name"));

  /* Adds the length of the line in Pixels, e.g. "B1 - Wienerstraße: 5.43" */
  text: eval(prop("text") . ": " . line_length(prop("geo")));

  /* Only the first 20px of the line should be rendered */
  geo: eval(line_part(prop("geo"), 0, 20));

  /* Width: Render the line 30m wide - ATTENTION: this statement works only with Mapnik >= 3.0 */
  width: eval(metric("30m"));
}
```

  In fact you can write the last line as "width: 30m;" as pgmapcss supports other units than pixels. (Still it needs Mapnik >= 3.0, as older mapnik versions can't read the width of a line from a database column). (As of this writing in January 2014 there is only one [specific mapnik branch](https://github.com/mapnik/mapnik/tree/stroke-width-expr) which supports this feature, although the [expr-v2 branch](https://github.com/mapnik/mapnik/tree/expr-v2) is expected to support it soon).

  Starting with version 0.7, pgmapcss does not require eval(...) to be wrapped around expressions, but for compatibility with other MapCSS implementations you should write it out.

  See [the "eval" documentation](doc/eval.creole) for a complete list of functions.

### Combine features: ###

  Often it makes sense to combine similar features, e.g. streets which are split into short parts due to changes in their street layout. This results in missing street names as the parts are too small. With pgmapcss you can combine those map features, so that the name can span the whole street.

### Relate neighbouring map features: ###

  Set neighbouring map features into relation. Map features don't exist independent from their surroundings. This can be done using the "near" link syntax. This is a pgmapcss specific enhancement.

  Example:
```css
/* This selector selects the closest highway for each restaurant. These
selectors always need the be read from right to left, as the last object is the
one the selector shapes (as in normal CSS) */

line[highway] near[index=0] point[amenity=restaurant] {
  /* Prints the name of the restaurant plus "near" plus the name of the highway
  plus the distance to the highway in meters in brackets. */
  text: eval(
    tag("name") .  " near " .
    parent_tag("name") .
    " (" . metric(link_tag("distance", "m")) . "m)"
  );
}
```

### Included Icon set: ###
pgmapcss includes the [Mapbox Maki Icon Set](https://www.mapbox.com/maki/). So for simple styles you don't need to create own icons.

Example:
```css
node|z14-[amenity=bicycle_parking] {
  icon-image: bicycle;
  icon-width: 18;      /* default: 24; valid values: 12, 18, 24 */
  icon-color: #ff0000; /* default #404040 */
}
```
* [Try it online!](http://pgmapcss.openstreetbrowser.org/?style=e8110&zoom=14&lat=48.2098&lon=16.3725)

Current limitations: Only the widths 12, 18 and 24 are supported right now, which are the sizes of the icon set. Scaling for icons (also custom icons) is not implemented right now.

[List of currently available icons](doc/Mapbox_Maki_icons.md). If an icon is missing, Mapbox Maki is Open Source; you can [contribute icons](https://github.com/mapbox/maki), they will be included in the next pgmapcss release.

### pgmapcss is (mostly) fast: ###

Optimized database queries: Only those map features which are visible in the current zoom level are requested from the database.

The compiled database function uses PL/Python3 database language, which makes execution efficient and powerful.

As Mapnik 2.x can't read symbolizer values (like color, width, ...) from database columns, the mapnik pre-processor has to create style rules for all possible value combinations. The more complex the style sheet, the larger the mapnik style files and therefore rendering can take a long time. The up-coming Mapnik 3.0 should solve these issues.

### Easy to install: ###

Find installation instructions in [Install pgmapcss with Mapnik 2.2 on Ubuntu 12.04](doc/Install pgmapcss with Mapnik_2.2 on Ubuntu_12.04.md).

There's a file [test.mapcss](./test.mapcss) which you can use to build upon. You can [try it online!](http://pgmapcss.openstreetbrowser.org/?style=d9c30&zoom=14&lat=48.2098&lon=16.3725)

Share this
----------
* [Flattr this!](https://flattr.com/submit/auto?user_id=plepe&url=https://github.com/plepe/pgmapcss&title=PGMapCSS&language=&tags=github&category=software)
* [Fork me on GitHub](https://github.com/plepe/pgmapcss)
