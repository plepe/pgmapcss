#!/bin/bash

for i in \
  pgmapcss_types.sql \
  pgmapcss_condition.sql \
  pgmapcss_parse_selector.sql \
  pgmapcss_parse_selectors.sql \
  pgmapcss_parse_properties.sql \
  pgmapcss_build_statement.sql \
  pgmapcss_compile_content.sql \
  pgmapcss_compile.sql \
  pgmapcss_install.sql
do
  echo "* $i"
  psql $@ -f $i
done

FILE=`cat test.mapcss`
psql $@ -c "select pgmapcss_install('test', \$\$$FILE\$\$);"

psql $@ -c "select * from css_check_test('N1234', 'highway=>primary, name=>Testroad', null, Array['way','line'], 25000);"
psql $@ -c "select * from css_check_test('N1234', 'highway=>primary, bridge=>yes, name=>Testroad', null, Array['way','line'], 25000);"
