#!/bin/bash

for i in \
  array_search.sql \
  pgmapcss_types.sql \
  objects_osm2pgsql.sql \
  pgmapcss_render_context.sql \
  pgmapcss_object.sql \
  pgmapcss_parse_string.sql \
  pgmapcss_parse_condition.sql \
  pgmapcss_parse_comments.sql \
  pgmapcss_parse_selector_part.sql \
  pgmapcss_parse_selectors.sql \
  pgmapcss_compile_condition.sql \
  pgmapcss_compile_conditions.sql \
  pgmapcss_compile_selector_part.sql \
  pgmapcss_parse_properties.sql \
  pgmapcss_build_statement.sql \
  pgmapcss_compile_content.sql \
  pgmapcss_parse_eval.sql \
  pgmapcss_compile_eval.sql \
  pgmapcss_compile_where.sql \
  eval.sql \
  pgmapcss_compile.sql \
  pgmapcss_install.sql
do
  echo "* $i"
  psql $@ --set ON_ERROR_STOP=1 -f src/$i
  ERR=$?

  if [ $ERR -ne 0 ] ; then
    echo
    echo "Aborting install.sh due to error!"
    exit $ERR
  fi
done
