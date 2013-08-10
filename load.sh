#!/bin/bash

echo "=== Resulting function ===" > test.output
FILE=`cat test.mapcss`
psql $@ --set ON_ERROR_STOP=1 -P format=unaligned -c "select pgmapcss_install('test', \$\$$FILE\$\$);" | tail -n+2 | head -n-2 >> test.output
ERR=$?

if [ $ERR -eq 0 ] ; then
  less test.output
else
  echo "An error occured when compiling CSS file"
  exit $ERR
fi

./preprocess_colors.pl
