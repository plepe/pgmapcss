#!/bin/bash

for i in \
  pgmapcss_condition.sql \
  pgmapcss_parse_selector.sql \
  pgmapcss_parse_selectors.sql \
  pgmapcss_parse_properties.sql \
  pgmapcss_build_statement.sql \
  pgmapcss_compile_content.sql \
  pgmapcss_compile.sql
do
  echo "* $i"
  psql $@ -f $i
done
