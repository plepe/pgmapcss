#!/bin/bash

rm -f test.output

echo "* Compiling mapcss file"
FILE=`cat default.mapcss test.mapcss`
psql $@ --set ON_ERROR_STOP=1 -P format=unaligned -c "select pgmapcss_install('test', \$\$$FILE\$\$);" 2> test.stderr | tail -n+2 | head -n-2 >> test.stdout

echo "* Pre-processing mapnik file"
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
