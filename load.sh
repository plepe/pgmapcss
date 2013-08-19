#!/bin/bash

function show_usage {
  echo
  echo "Usage:"
  echo "  load.sh [option...] style_id"
  echo
  echo "  style_id is a required argument. The compiled functions will be prefixed "
  echo "  by 'style_id', e.g. 'style_id_match()'."
  echo
  echo "Options:"
  echo "  -d, --database    Name of database (default: username)"
  echo "  -u, --user        User for database (default: username)"
  echo "  -p, --password    Password for database (default: PASSWORD)"
  echo "  -h, --host        Host for database (default: localhost)"
  echo "  -f, --file        File to load (default: 'style_id'.mapcss)"
  echo "  -b, --base        mapcss/mapnik file building the base for the style "
  echo "                    (default: 'default' in the directory of load.sh; you "
  echo "                    may specify an absolute path)"
}

ARGS=$(getopt -o d:u:p:h:f:b: -l "database:,user:,password:,host:,file:,base:" -n "load.sh" -- "$@");

if [ $? -ne 0 ] ; then
  show_usage
  exit 1
fi

eval set -- "$ARGS";

DB=$USER
DBUSER=$USER
DBPASS="PASSWORD"
DBHOST="localhost"
FILE=""
BASE="$(dirname $0)/default"

while true ; do
  case "$1" in
    -d|--database)
      shift;
      DB=$1
      shift;
      ;;
    -u|--user)
      shift;
      DBUSER=$1
      shift;
      ;;
    -p|--password)
      shift;
      DBPASS=$1
      shift;
      ;;
    -h|--host)
      shift;
      DBHOST=$1
      shift;
      ;;
    -f|--file)
      shift;
      FILE=$1
      shift;
      ;;
    -b|--base)
      shift;
      BASE=$1
      shift;
      ;;
    --)
      shift;
      break;
      ;;
  esac
done

STYLE_ID=$@
if [ "$STYLE_ID" == "" ] ; then
  print "No style_id supplied"
  show_usage
  exit;
fi

if [ "$FILE" == "" ] ; then
  FILE="$STYLE_ID.mapcss"
fi

rm -f $STYLE_ID.output

echo "* Compiling mapcss file"
CONTENT=`cat $BASE.mapcss $FILE`
psql -d "dbname=$DB user=$DBUSER host=$DBHOST password=$DBPASS" --set ON_ERROR_STOP=1 -P format=unaligned -c "select pgmapcss_install('$STYLE_ID', \$\$$CONTENT\$\$);" 2> $STYLE_ID.stderr | tail -n+2 | head -n-2 >> $STYLE_ID.stdout

echo "* Pre-processing mapnik file"
./preprocess.pl >> $STYLE_ID.stderr

if [ -s $STYLE_ID.stderr ] ; then
  echo "--=== Warnings and Errors ===--" >> $STYLE_ID.output
  cat $STYLE_ID.stderr >> $STYLE_ID.output
fi

echo "--=== Resulting functions ===--" >> $STYLE_ID.output
cat $STYLE_ID.stdout >> $STYLE_ID.output

rm $STYLE_ID.stderr
rm $STYLE_ID.stdout

less $STYLE_ID.output
