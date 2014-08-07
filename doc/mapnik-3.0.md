This is the list of properties when using Mapnik 3.0 (or the master development version as of May 6, 2014) (use -t mapnik-3.0 when loading mapcss file). 

* The value of properties marked with an asterisk (*) in the "Compatibility MapCSS 0.2" column need to be predictable at compile-time; if not, a warning will be issued when compiling. Features might be missing in the rendered image.

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

| CSS parameter | Description | Default value | Compatibility MapCSS 0.2 |
|---------------|-------------|---------------|--------------------------|
| fill-color | The color of the background | 0% (transparent) | YES(*)
| fill-image | an image for the background instead of a color fill | | YES(*)
| buffer | set the buffer-size of the Map | 0 | no standard(*)

* MapCSS 0.2 properties not (yet) supported: antialiasing (always fully antialiased), fill-opacity (use alpha-channel on fill-color instead)

Point properties
----------------

| CSS parameter | Description | Default value | Compatibility MapCSS 0.2 |
|---------------|-------------|---------------|--------------------------|
| icon-image | URL (absolute or relative) of an image to use as an icon, e.g. url('img/foo.svg'). Icons from [Mapbox Maki](https://www.mapbox.com/maki/) project can be included via their ID, e.g. parking-garage. | | YES
| icon-color | Only for icons from Mapbox Maki project! Change color of icon to given color. | #444444. | no standard(*)
| icon-opacity | Opacity of the icon image | 100% (opaque) | YES(*)
| icon-width | Width of image. Ignored for custom images. For icons from Mapbox Maki project values 12, 18 or 24 have to be used. | 24 | PARTLY
| icon-height | Height of image. Ignored. | - | -- | NO
| icon-rotation | Rotation of the image in the current angular system. | 0 | NO
| symbol-shape | Display a symbol at the position of the point. Supported values: square, circle, triangle, pentagon, hexagon, heptagon, octagon, nonagon, decagon | - | NO, JOSM (*)
| symbol-size | Size of the symbol (px) | 10 | NO, JOSM (*)
| symbol-stroke-width | outline stroke width | 1 | NO, JOSM (*)
| symbol-stroke-color | line color | #FFC800 | NO, JOSM (*)
| symbol-stroke-opacity | line opacity | 1.0 | NO, JOSM (*)
| symbol-fill-color | fill color for the shape | #0000FF | NO, JOSM (*)
| symbol-fill-opacity | fill opacity | 1.0 | NO, JOSM (*)
| symbol-rotation | Rotation of the symbol in the current angular system. | 0 | NO

Line properties
---------------

| CSS parameter | Description | Default value | Compatibility MapCSS 0.2 |
|---------------|-------------|---------------|--------------------------|
| color | Colour of the line. | | YES
| width | The line width in pixels. | | YES
| offset | Pixels to offset the line to the left or right. | 0 | no standard
| opacity | How transparent the line is, from 0 (transparent) to 1 (opaque). | 1 | YES
| image |  The URL of an image to use for filling the line | | YES
| linejoin | The style for line corners: 'round', 'miter' or 'bevel'. | round | YES
| linecap | The style for the end of the line: 'none' (default), 'round' or 'square' | none | YES
| miterlimit | Applies for linejoin: miter. Sets the maximum overshoot when line segments meet at a very small angle | 4.0 | no standard, JOSM
| dashes | An array of alternating on/off lengths | | YES(*)
| dashes-background-color | The color to use in between the dashes (optional) | | NO, JOSM
| repeat-image | Repeated image along a line (actually similar to "image", but with more features and compatible to JOSM) | | JOSM
| repeat-image-offset | Offset from the line | value of `offset` | JOSM (*)
| repeat-image-align | Alignment of the image. Top-, bottom edge or the (horizontal) center line of the image will be along the line. Values: 'top', 'center', bottom' | center | JOSM
| casing-dashes-background-opacity | Opacity value for the dashes background (optional) | | NO, JOSM
| casing-color | Colour of the casing (border) of a line. | | YES
| casing-width | Width of the casing (border) of the line (added to 'width' of the line). | 0 | YES
| casing-offset | Pixels to offset the casing of the line to the left or right. | value of `offset` | no standard
| casing-opacity | How transparent the casing is, from 0 (transparent) to 1 (opaque). | 1 | YES
| casing-linejoin | The style for casing corners: 'round', 'miter' or 'bevel'. | value of `linejoin` | YES
| casing-linecap | The style for the end of the casing: 'none', 'round' or 'square' | value of `linecap`| YES
| casing-dashes | An array of alternating on/off lengths | | YES(*)
| casing-dashes-background-color | The color to use in between the dashes (optional) | | NO, JOSM
| casing-dashes-background-opacity | Opacity value for the dashes background (optional) | | NO, JOSM
| left-casing-* | Draw a line to to the left of the main line; uses the same suffixes as casing-* | | NO, JOSM
| right-casing-* | Draw a line to to the right of the main line; uses the same suffixes as casing-* | | NO, JOSM

* MapCSS 0.2 properties not (yet) supported: extrude, extrude-*

Area properties
---------------

| CSS parameter | Description | Default value | Compatibility MapCSS 0.2 |
|---------------|-------------|---------------|--------------------------|
| fill-color | Colour in which to fill the area. | | YES
| fill-opacity | How transparent the fill is, from 0 (transparent) to 1 (opaque) | 1 | YES(*)
| fill-image |  The URL of an image to use for filling the area | | YES

Label properties
----------------

| CSS parameter | Description | Default value | Compatibility MapCSS 0.2 |
|---------------|-------------|---------------|--------------------------|
| max-width | The maximum width of a text label for a point, after which it should wrap onto the next line. | | YES(*)
| text-offset | The vertical offset from the centre of the way or point. By default relative to an icon/symbol (see text-anchor-vertical) | 0 | YES(*)
| text-anchor-vertical | vertical text label placement relative to icon/symbol, possible values (below, above) | below | NO, JOSM (*)
| text-anchor-horizontal | Position of label relative to point position (left, middle, right) | middle | NO, JOSM (*)
| text-position | Whether the text follows the path of the way ('line') or is centred on the area ('center') | center | YES
| font-family | Name of the font to use default (see 'Fonts' below) | DejaVu Sans | YES(*)
| font-weight |  'bold' or 'normal' | normal | YES
| font-style |  'italic' or 'normal' | normal | YES
| font-size | Size of the text | 12 | YES
| text-color | Colour of text | #000000 | YES
| text-halo-color | The colour (hex or CSS) of the 'halo' or 'pull-out' used to make the text stand out from features underneath it. | #ffffff | YES
| text-halo-radius |  The radius of the halo | 0 | YES
| text | A tag from which text for label will be read, or (if quoted or an eval-statement) the text for the label | | YES
| text-spacing | Space between repeated labels. If spacing is 0 only one label is placed. | 0 | no standard(*)
| text-transform |  'none', 'uppercase', 'lowercase', 'capitalize' | none | YES
| text-opacity | How transparent the text is, from 0 (transparent) to 1 (opaque) | 1 | YES
| character-spacing | Additional horizontal spacing between characters. | 0 | no standard

* MapCSS 0.2 properties not (yet) supported: font-variant, text-decoration
* Properties removed in Mapnik 3.0: wrap-character

Shields
-------

| CSS parameter | Description | Default value | Compatibility MapCSS 0.2 |
|---------------|-------------|---------------|--------------------------|
| shield-placement | Whether the shields follows the path of the way ('line') or is centred on the area ('point') | 'line' for lines, 'point' for other features | no standard(*)
| shield-font-family | Name of the font to use | value of font-family | no standard(*)
| shield-font-weight |  'bold' or 'normal' | value of font-weight | no standard(*)
| shield-font-style |  'italic' or 'normal' | value of font-style | no standard(*)
| shield-font-size | Size of the text | value of font-size | no standard(*)
| shield-text-color | Colour of text | #000000 | no standard(*)
| shield-text-halo-color | The colour (hex or CSS) of the 'halo' or 'pull-out' used to make the text stand out from features underneath it. | #ffffff | no standard(*)
| shield-text-halo-radius |  The radius of the halo | 0 | no standard(*)
| shield-text | A tag from which text for label will be read, or (if quoted or an eval-statement) the text for the label | | YES
| shield-spacing | Space between repeated shields. If spacing is 0 only one label is placed | 196 | no standard(*)
| shield-opacity |  How transparent the shield is, from 0 (transparent) to 1 (opaque) | 1 | YES(*)
| shield-image |  The URL (absolute or relative) of an image to use as a background for text. | | YES
| shield-text-transform |  'none', 'uppercase', 'lowercase', 'capitalize' | value of text-transform | no standard

* MapCSS 0.2 properties not (yet) supported: shield-color, shield-frame-color, shield-frame-width, shield-casing-color, shield-casing-width, shield-shape.
* Currently a shield-image is mandatory.

Fonts
-----

There's a fontset for each font-family / font-weight / font-style combination, defined in default-template.mapnik. There's a default fallback to unifont too (which might change in the future). The name of the fontsets is "font-family - font-weight - font-style", e.g. "DejaVu Serif Condensed - bold - italic".

Also all possible font-families are defined in default.mapcss in the @values font-family clause.
