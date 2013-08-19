#!/bin/bash

rm -f test.output

FILE=`cat test.mapcss`
psql $@ --set ON_ERROR_STOP=1 -P format=unaligned -c "select pgmapcss_install('test', \$\$$FILE\$\$);" 2> test.stderr | tail -n+2 | head -n-2 >> test.stdout

./preprocess.pl >> test.stderr

if [ -s test.stderr ] ; then
  echo "--=== Warnings and Errors ===--" >> test.output
  cat test.stderr >> test.output
fi

echo "--=== Resulting functions ===--" >> test.output
cat test.stdout >> test.output

rm test.stderr
rm test.stdout

less test.output
