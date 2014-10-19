This is the list of properties when using OpenLayers 3.0 with ol4pgm (use -t ol4pgm when loading mapcss file). [ol4pgm](https://github.com/plepe/ol4pgm) is an interactive frontend for pgmapcss's standalone mode using OpenLayers 3.0.

Rendering order
---------------

In contrast to the [MapCSS 0.2 specification](https://wiki.openstreetmap.org/wiki/MapCSS/0.2#Rendering_Order) the following rendering order is used:

1. Objects with lower layer (see below) should always be rendered first.
2. Within a layer, first all fills are rendered, then all casings, then all strokes.
3. Within each of those categories, objects are ordered according to z-index.
4. If all of the above are equal, the order is undefined.

Finally:
* By default, all icons are rendered as if they are on layer 100 (defined by property 'point-layer')
* By default, all labels with text-position!=line are rendered as if they are on layer 101 (defined by property 'point-text-layer')
* By default, all labels with text-position=line are rendered as if they are on layer 102 (defined by property 'line-text-layer')
* By default, all shields are rendered as if they are on layer 103 (defined by property 'shield-layer')

General properties
------------------

| CSS parameter | Description | Default value | Compatibility MapCSS 0.2 |
|---------------|-------------|---------------|--------------------------|
| layer | the highest level of ordering objects | the value of tag 'layer' (or 0) | see below
| [style_element]-layer | override layer property for a specific style_element | the value of property 'layer' or the values as described under 'Rendering order' | NO
| z-index | specify the order of objects in each layer: The objects with higher z-index are drawn on top of objects with lower z-index | 0 | YES

* Property 'layer': MapCSS 0.2 does define the rendering order dependend on the layer-tag of the objects, but does not define a way to change that order from the stylesheet.

Canvas properties
-----------------

No canvas properties are supported right now.

Point properties
----------------

| CSS parameter | Description | Default value | Compatibility MapCSS 0.2 |
|---------------|-------------|---------------|--------------------------|
| icon-image | URL (absolute or relative) of an image to use as an icon, e.g. url('img/foo.svg'). Icons from [Mapbox Maki](https://www.mapbox.com/maki/) project can be included via their ID, e.g. parking-garage. | | YES
| icon-color | Only for icons from Mapbox Maki project! Change color of icon to given color. | #444444. | no standard(*)
| icon-width | Width of image. Ignored for custom images. For icons from Mapbox Maki project values 12, 18 or 24 have to be used. | 24 | PARTLY
| icon-height | Height of image. Ignored. | - | -- | NO
| icon-rotation | Rotation of the image in the current angular system. | 0 | NO
| symbol-shape | Display a symbol at the position of the point. Supported values: square, circle, triangle, pentagon, hexagon, heptagon, octagon, nonagon, decagon | - | NO, JOSM (*)
| symbol-size | Size of the symbol (px) | 10 | NO, JOSM (*)
| symbol-stroke-width | outline stroke width | 1 | NO, JOSM (*)
| symbol-stroke-color | line color | #FFC800 | NO, JOSM (*)
| symbol-fill-color | fill color for the shape | #0000FF | NO, JOSM (*)
| symbol-rotation | Rotation of the symbol in the current angular system. | 0 | NO

Line properties
---------------

| CSS parameter | Description | Default value | Compatibility MapCSS 0.2 |
|---------------|-------------|---------------|--------------------------|
| color | Colour of the line. | | YES
| width | The line width in pixels. | | YES
| linejoin | The style for line corners: 'round', 'miter' or 'bevel'. | round | YES
| linecap | The style for the end of the line: 'none' (default), 'round' or 'square' | none | YES
| miterlimit | Applies for linejoin: miter. Sets the maximum overshoot when line segments meet at a very small angle | 4.0 | no standard, JOSM
| dashes | An array of alternating on/off lengths | | YES(*)
| dashes-background-color | The color to use in between the dashes (optional) | | NO, JOSM
| casing-color | Colour of the casing (border) of a line. | | YES
| casing-width | Width of the casing (border) of the line (added to 'width' of the line). | 0 | YES
| casing-linejoin | The style for casing corners: 'round', 'miter' or 'bevel'. | value of `linejoin` | YES
| casing-linecap | The style for the end of the casing: 'none', 'round' or 'square' | value of `linecap`| YES
| casing-dashes | An array of alternating on/off lengths | | YES(*)
| casing-dashes-background-color | The color to use in between the dashes (optional) | | NO, JOSM

Area properties
---------------

| CSS parameter | Description | Default value | Compatibility MapCSS 0.2 |
|---------------|-------------|---------------|--------------------------|
| fill-color | Colour in which to fill the area. | | YES

Label properties
----------------

| CSS parameter | Description | Default value | Compatibility MapCSS 0.2 |
|---------------|-------------|---------------|--------------------------|
| text-offset | The vertical offset from the centre of the way or point. By default relative to an icon/symbol (see text-anchor-vertical) | 0 | YES(*)
| text-anchor-vertical | vertical text label placement relative to icon/symbol, possible values (below, above) | below | NO, JOSM (*)
| text-anchor-horizontal | Position of label relative to point position (left, middle, right) | middle | NO, JOSM (*)
| font-family | Name of the font to use default (see 'Fonts' below) | DejaVu Sans | YES(*)
| font-size | Size of the text | 12 | YES
| text-color | Colour of text | #000000 | YES
| text-halo-color | The colour (hex or CSS) of the 'halo' or 'pull-out' used to make the text stand out from features underneath it. | #ffffff | YES
| text-halo-radius |  The radius of the halo | 0 | YES
| text | A tag from which text for label will be read, or (if quoted or an eval-statement) the text for the label. If value is 'auto', one of the following tags will be used: "name:" + LANG, "name", "int_name", "ref", "operator", "brand" and "addr:housenumber". | | YES
| text-transform |  'none', 'uppercase', 'lowercase', 'capitalize' | none | YES
