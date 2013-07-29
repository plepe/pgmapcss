psql $@ -c "select * from css_check_test('N1234', 'highway=>primary, name=>Testroad', null, Array['way','line'], 25000);"
psql $@ -c "select * from css_check_test('N1234', 'highway=>primary, bridge=>yes, name=>Testroad', null, Array['way','line'], 25000);"
psql $@ -c "select * from css_check_test('N1234', 'highway=>residential, bridge=>yes, name=>Testroad', null, Array['way','line'], 25000);"

psql $@ -c "select (css_check_test(cast(osm_id as text), tags, way, Array['way','line'], 25000)).*, osm_id, tags, way from planet_osm_line;"
