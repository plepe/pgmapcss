== josm ==
Improves compatibility with JOSM:
* "set foo" implies "set .foo" (class is set too)
* Assume black as background color, use white texts per default
* Areas have a 0.3 (?) opacity per default
* Labels and icons may overlap
* Uses radians as angular system
* Some other minor changes to default values (e.g. font-size, linecap, ...)

== overpass-turbo ==
pgmapcss does not support the Overpass API query language. Therefore you need
to use MapCSS as query language. In pgmapcss, MapCSS Rules load data from database if they use certain properties, e.g. 'text', 'width' or 'fill-color'. E.g. an object which just have a 'color', but not a 'width' will not be displayed, and therefore it is not even requestes from the database. If you use the following mapcss code, this will load all restaurants from database, label them and apply the default overpass-turbo style to it.
```css
node[amenity=restaurant] {
  text: name;
}
```
* All nodes will be changed to circular areas with 9px radius (therefore a fill-color, width and color can be applied)
* All objects which are loaded from the database get some default style.
