#!/bin/sh

for i in `ls *mapcss` ; do
  F=$(echo $i | cut -d. -f1)

  cat $F.md
  echo
  echo "![$F]($F.png)"
  echo "\`\`\`css"
  cat $F.mapcss
  echo "\`\`\`"
  echo
done
