#!/bin/sh

for i in \
  roads_parks.mapcss \
  motorway_junction.mapcss \
  places_population.mapcss \
  highest_peaks.mapcss \
  highest_peaks_var.mapcss \
  housenumbers.mapcss \
  combined_roads.mapcss \
  tramway_network.mapcss \
  ; do
  F=$(echo $i | cut -d. -f1)

  cat $F.md
  echo
  echo "![$F]($F.png)"
  echo "\`\`\`css"
  cat $F.mapcss
  echo "\`\`\`"
  echo
done

echo "Data: (c) [OpenStreetMap](http://www.openstreetmap.org) contributors."
