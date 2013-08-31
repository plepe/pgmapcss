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
  echo "  -h, --help        Help (this page)"
  echo "  -d, --database    Name of database (default: username)"
  echo "  -u, --user        User for database (default: username)"
  echo "  -p, --password    Password for database (default: PASSWORD)"
  echo "  -h, --host        Host for database (default: localhost)"
  echo "  -f, --file        File to load (default: 'style_id'.mapcss)"
  echo "  -b, --base        mapcss/mapnik file building the base for the style "
  echo "                    (default: 'default' in the directory of load.sh; you "
  echo "                    may specify an absolute path)"
}

ARGS=$(getopt -o hd:u:p:H:f:b: -l "help,database:,user:,password:,host:,file:,base:" -n "load.sh" -- "$@");

if [ $? -ne 0 ] ; then
  show_usage
  exit 1
fi

eval set -- "$ARGS";

export DB=$USER
export DBUSER=$USER
export DBPASS="PASSWORD"
export DBHOST="localhost"
export FILE=""
export BASE="$(dirname $0)/default"
export STYLE_ID=""

while true ; do
  case "$1" in
    -h|--help)
      shift;
      show_usage
      exit
      ;;
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
    -H|--host)
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

# if file name is accidentially given, cut '.mapcss'
if [ "$(echo $STYLE_ID | cut -d. -f2)" == "mapcss" ] ; then
  STYLE_ID=$(echo $STYLE_ID | cut -d. -f1)
fi

# if no file parameter was given use $STYLE_ID.mapcss
if [ "$FILE" == "" ] ; then
  FILE="$STYLE_ID.mapcss"
fi

# check if file exists
if [ ! -f $FILE ] ; then
  echo "No such file: $FILE"
  exit
fi

rm -f $STYLE_ID.output

echo "* Compiling mapcss file"
CONTENT=`cat $BASE.mapcss $FILE`
psql -d "dbname=$DB user=$DBUSER host=$DBHOST password=$DBPASS" --set ON_ERROR_STOP=1 -P format=unaligned -c "select pgmapcss_install('$STYLE_ID', \$\$$CONTENT\$\$);" 2> $STYLE_ID.stderr | tail -n+2 | head -n-2 >> $STYLE_ID.stdout

if [ -s $STYLE_ID.stdout ] ; then
  echo "* Pre-processing mapnik file"
  $(dirname $0)/preprocess.pl >> $STYLE_ID.stderr
fi

if [ -s $STYLE_ID.stderr ] ; then
  echo "--=== Warnings and Errors ===--" >> $STYLE_ID.output
  X=$(sed -n '/CONTEXT:/{:a;N;/PL\/pgSQL function/!ba;s/.*\n//};p' $STYLE_ID.stderr)

  echo $X >> $STYLE_ID.output
  echo $X
fi

if [ -s $STYLE_ID.stdout ] ; then
  echo "--=== Resulting functions ===--" >> $STYLE_ID.output
  cat $STYLE_ID.stdout >> $STYLE_ID.output
else
  echo "Compiling failed. See $STYLE_ID.output for details."
fi

rm $STYLE_ID.stderr
rm $STYLE_ID.stdout
