def compile_requirements(eval_options, prop, stat, indent=''):
    ret = ''

    if 'requirements' in eval_options:
        req = eval_options['requirements'] & { 'geo', 'meta' }
        checks = set()

        if len(req):
                if 'geo' in req:
                    checks.add("not 'geo' in current['object']")
                if 'meta' in req:
                    checks.add("not 'osm:version' in current['tags']")

                ret += indent + "if " + ' or '.join(checks) + ":\n"
                ret += indent + "    yield 'request', " + str(prop['id']) +\
                    ", " + repr({
                        'type': 'objects_by_id',
                        'options': eval_options,
                    }) + '\n'

        req = eval_options['requirements'] & { 'parent_geo' }
        if len(req):
                ret += indent + "objects_missing_geo = [ o[0] for o in objects if not 'geo' in o[0] ]\n"
                ret += indent + "plpy.warning([ o['id'] for o in objects_missing_geo ])\n"
                ret += indent + "if len(objects_missing_geo):\n"
                ret += indent + "    current['object']['parents'] = objects_missing_geo\n"
                ret += indent + "    yield 'request', " + str(prop['id']) +\
                    ", " + repr({
                        'type': 'parent_objects_by_id',
                        'options': eval_options,
                    }) + '\n'
                ret += indent + "    del current['object']['parents']\n"

    return ret
