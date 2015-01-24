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

    return ret
