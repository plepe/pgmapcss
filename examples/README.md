Major roads and parks
=====================
For starters a simple example will be shown: Major roads and parks.

![roads_parks](roads_parks.png)
```css
/* draw a green polygon for all parks */
area[leisure=park] {
  fill-color: #00af00;
}
/* print a label on all parks */
area[leisure=park]::label {
  text: eval(tag(name));
  font-family: "DejaVu Sans Oblique";
  font-size: 9;
  text-color: #005f00;
  z-index: 3;
}

/* all major roads will be rendered with a 2px black line */
line|z12-[highway=primary],
line|z12-[highway=secondary],
line|z12-[highway=tertiary] {
  color: #000000;
  width: 2;
  z-index: 1;
}
/* and a black label next to the line
   with a 50% transparent white halo */
line|z12-[highway=primary]::label,
line|z12-[highway=secondary]::label,
line|z12-[highway=tertiary]::label {
  text: eval(tag(name));
  text-offset: 9;
  text-color: #000000;
  text-halo-color: #ffffff7f;
  text-halo-radius: 1;
  line-position: line;
  z-index: 2;
}
```

Layering roads of a motorway junction
=====================================
This example shows how eval-statements for z-index can be used to layer roads correctly.

Warning: This example needs Mapnik branch 'stroke-width-expr' or version 3.0 and accompaning modifications in file default-template.mapnik (search for 'stroke-width-expr' for details). If you run this example with Mapnik 2.2 the casing might be missing.

![motorway_junction](motorway_junction.png)
```css
line[highway=motorway],
line[highway=trunk] {
  width: 4;
  set .major_road;
}
line[highway=motorway_link],
line[highway=trunk_link] {
  width: 2;
  set .major_road;
}
line.major_road {
  linecap: round;
  color: #ff0000;
  z-index: eval(any(tag('layer'), 0)+0.5);
}

line.major_road::casing {
  linecap: butt;
  width: eval(prop(width, default)+2);
  color: #707070;
  z-index: eval(any(tag('layer'), 0));
}
line.major_road[bridge]::casing {
  color: #000000;
}
line.major_road[tunnel] {
  color: #ff7f7f;
}
line.major_road[tunnel]::casing {
  dashes: 3, 3;
}
```

Place nodes and their population
================================
In the 3rd example we see the places names of some villages and a simple
diagram with the population size. Also the administrative boundaries are shown.

![places_population](places_population.png)
```css
/* Print the name of all places */
point[place] {
  text: eval(tag(name));
  z-index: 2;
}

/* For each place show a diagram: a red circle depending on the
  population of the place. We are using the square root of population
  as pixel radius to not grow too fast. */
point[place]::diagram {
  geo: eval(buffer(prop(geo), sqrt(tag(population))));
  fill-color: #ff7f7f;
  color: #ff0000;
  width: 1;
}

/* Also, show administrative boundaries as purple lines */
line[boundary=administrative][admin_level<=8],
relation[boundary=administrative][admin_level<=8] {
  color: #7f00ff;
  width: 1;
  z-index: 1;
}
```

Highest Peaks
=============
The following map shows how to build relationships to "nearby" objects. Every
(mountain?) peak is compared to the surrounding peaks (with a distance of up to
128px) and if the peak is the highest it is highlighted.


![highest_peaks](highest_peaks.png)
```css
/* For every peak find all other peaks in a distance of max. 128px and
   build a list of the other peak's elevation in tag 'near_ele' */
node[natural=peak] near[distance<128] node[natural=peak] {
  set near_ele = eval(push(tag(near_ele), parent_tag(ele)));
}

/* For every peak calculate the max elevation of the nearby peaks and save in
   tag 'max_near_ele'. Write name and elevation on the peak. */
node[natural=peak] {
  set max_near_ele = eval(max(tag(near_ele)));
  text: eval(concat(tag(name), ' (', tag(ele), ')'));

/* For debugging you could uncomment the following row. It print the elevation
   of nearby peaks into a second second row. */
// text: eval(concat(tag(name), ' ', tag(ele), '\n(', join(tag(near_ele), ', '), ')'));
  z-index: 4;

  icon-image: highest_peaks_small.svg;
  text-offset: 7;
}

/* if this is the highest peak of all neighbouring peaks OR the only peak,
   print name in red and in larger font. Also write name earlier to have higher
   preference (z-index). */
node[natural=peak][ele>=eval(tag(max_near_ele))],
node[natural=peak][!near_ele] {
  font-size: 14;
  text-color: red;
  z-index: 3;

  icon-image: highest_peaks_large.svg;
  text-offset: 8;
}
```

Combining street parts
======================
Streets in OpenStreetMap are usually split into short junks to reflect changes in street layout: one way streets, bus routes, lanes, bicycles lanes, ... This raises a problem when rendering roads, as labels are missing (because they don't fit in a zoom level on the road) or are repeated at random intervals (when they just fit onto roads). pgmapcss 0.3 introduces 'combine', where features can be merged by statements.

In this example features are merged by either major/minor road type and their name. In the left image features are not merged. The change in the right image is clearly visible, much more roads can be labeled.

![combined_roads](combined_roads.png)
```css
line[highway=primary],
line[highway=secondary],
line[highway=tertiary] {
  set street_type = major;
}
line[highway=unclassified],
line[highway=residential] {
  set street_type = minor;
}

/* This is where the magic happens: At type 'street' is introduced
   which combines all lines with an equal 'street_type' tag (which
   is set in the statements above) and the same name. */
line[street_type] {
  combine street eval(concat(tag(street_type), '-', tag(name)));
}

street[street_type]::casing {
  color: #a0a0a0;
  z-index: -1;
}
street[street_type=major]::casing { width: 10; }
street[street_type=minor]::casing { width: 8; }

street[street_type=major] {
  width: 8;
  color: #ffff00;
  z-index: 0.1;
}
street[street_type=minor] {
  width: 6;
  color: #ffffff;
}

/* merge lines if possible; print name */
street::label {
  geo: eval(line_merge(prop(geo)));
  text: eval(tag(name));
  text-position: line;
  text-spacing: 256;
  z-index: 1;
}
```

Tramway network
===============
A route map of all tramway routes (and other means of transportation, but this should just be a simple example) should show all route references on their ways nicely sorted.

Also most stations consist of many individual stops for all the busses and trams going in different directions, but on the map we want to print the name only once.

This is something that usually needs quite some database magic, but can be achieved with some pgmapcss magic.

![tramway_network](tramway_network.png)
```css
/* Draw all tram routes in red */
line[route=tram] {
  color: #ff0000;
  width: 2;
}

/* For every route iterate over all members to save their 'ref' tag
   to the child tag 'ref_list' */
relation[route=tram] > line|z14-[railway] {
  set ref_list = eval(push(tag(ref_list), parent_tag(ref)));
}

/* Remove duplicate refs from list, sort the list. Combine all lines
   with the same combination of routes into a new type 'tram_routes'. */
line|z14-[railway] {
  set ref_list = eval(sort(unique(tag(ref_list))));
  combine tram_routes eval(tag(ref_list));
}

/* Render the tram_routes from the statement before. "Line Merge" the
   geometry for nicer label placement. Sort the refs "naturally" and
   merge with a colon. Repeat labels every ~128px. */
tram_routes::label {
  geo: eval(line_merge(prop(geo)));
  text: eval(join(natsort(tag(ref_list)), ', '));
  text-color: #ff0000;
  text-halo-color: #ffffff;
  text-halo-radius: 1;
  text-position: line;
  text-spacing: 128px;
  z-index: 3;
}

/* Find all tram stops on the map and combine them (with the same name - only
   if they have a name) to the new type 'tram_stop'. */
node|z14-[railway=tram_stop][name] {
  combine tram_stop eval(tag(name));
}

/* Build a polygon (a "convex hull") from all the tram stop nodes and
   draw a buffer of 7px around them. */
tram_stop {
  geo: eval(buffer(convex_hull(prop(geo)), 7px));
  fill-color: #a0a0a07f;
  width: 1;
  color: #a0a0a0af;
  z-index: 1;
}

/* Print the stop name on the polygon from the geometry of the "default"
   pseudo element (the statement above) */
tram_stop::label {
  geo: eval(prop(geo, default));
  text: eval(tag(name));
  z-index: 2;
}
```

Data: (c) [OpenStreetMap](http://www.openstreetmap.org) contributors.
