#!/bin/bash

echo "=== Resulting function ===" > test.output
FILE=`cat test.mapcss`
psql $@ -P format=unaligned -c "select pgmapcss_install('test', \$\$$FILE\$\$);" | tail -n+2 | head -n-2 >> test.output

less test.output
