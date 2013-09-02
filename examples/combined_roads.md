Combining street parts
======================
Streets in OpenStreetMap are usually split into short junks to reflect changes in street layout: one way streets, bus routes, lanes, bicycles lanes, ... This raises a problem when rendering roads, as labels are missing (because they don't fit in a zoom level on the road) or are repeated at random intervals (when they just fit onto roads). pgmapcss 0.3 introduces 'combine', where features can be merged by statements.

In this example features are merged by either major/minor road type and their name. In the left image features are not merged. The change in the right image is clearly visible, much more roads can be labeled.
