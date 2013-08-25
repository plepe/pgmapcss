#!/bin/bash

function show_usage {
  echo
  echo "Usage:"
  echo "  install.sh [option...]"
  echo
  echo "Options:"
  echo "  -h, --help        Help (this page)"
  echo "  -d, --database    Name of database (default: username)"
  echo "  -u, --user        User for database (default: username)"
  echo "  -p, --password    Password for database (default: PASSWORD)"
  echo "  -H, --host        Host for database (default: localhost)"
}

ARGS=$(getopt -o hd:u:p:H:f:b: -l "help,database:,user:,password:,host:" -n "install.sh" -- "$@");

if [ $? -ne 0 ] ; then
  show_usage
  exit 1
fi

eval set -- "$ARGS";

DB=$USER
DBUSER=$USER
DBPASS="PASSWORD"
DBHOST="localhost"
BASEPATH=$(dirname $0)

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
    --)
      shift;
      break;
      ;;
  esac
done


for i in \
  array_search.sql \
  natcasesort.sql \
  pgmapcss_types.sql \
  objects_osm2pgsql.sql \
  pgmapcss_render_context.sql \
  pgmapcss_object.sql \
  pgmapcss_parse_string.sql \
  pgmapcss_parse_condition.sql \
  pgmapcss_parse_comments.sql \
  pgmapcss_parse_selector_part.sql \
  pgmapcss_parse_selectors.sql \
  pgmapcss_parse_content.sql \
  pgmapcss_compile_condition.sql \
  pgmapcss_compile_conditions.sql \
  pgmapcss_compile_selector_part.sql \
  pgmapcss_parse_properties.sql \
  pgmapcss_compile_statement.sql \
  pgmapcss_compile_content.sql \
  pgmapcss_parse_eval.sql \
  pgmapcss_compile_eval.sql \
  pgmapcss_compile_where.sql \
  eval.sql \
  pgmapcss_compile.sql \
  pgmapcss_install.sql
do
  echo "* $i"
  psql -d "dbname=$DB user=$DBUSER host=$DBHOST password=$DBPASS" --set ON_ERROR_STOP=1 -f "$BASEPATH/src/$i"
  ERR=$?

  if [ $ERR -ne 0 ] ; then
    echo
    echo "Aborting install.sh due to error!"
    exit $ERR
  fi
done
