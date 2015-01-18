Highest Peaks (using global variables)
======================================
This is an optimized version of the "Highest Peak" above. In this example, not the relationship between nearby peaks is used, instead all peaks in the bounding box are sorted by elevation descending and the geometry of the peaks are collected in a global variable. If the buffer around the "current" peak intersects any peaks in the global variable, it is not the highest in the area.

This is much more performant as the original approach, where the nearest peaks for each peak had to be queried and compared. The main difference in the output is, that peaks outside the bounding box are not incorporated.

These features (order by value, global variables, collecting geometries) were introduced in version 0.11.
