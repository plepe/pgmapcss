psql $@ -c "select * from css_check_test(pgmapcss_object('N1234', 'highway=>primary, name=>Testroad', null, Array['way','line']), pgmapcss_render_context(null, 25000));"
psql $@ -c "select * from css_check_test(pgmapcss_object('N1234', 'highway=>residential, bridge=>yes, name=>Testroad', null, Array['way','line']), pgmapcss_render_context(null, 5000));"

psql $@ -c "select (css_check_test(pgmapcss_object(cast(osm_id as text), tags, way, Array['way','line']), pgmapcss_render_context(null, 25000))).*, osm_id, tags, way from planet_osm_line;"
