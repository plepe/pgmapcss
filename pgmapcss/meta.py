import pgmapcss.eval

def get_meta_from_code(style_id, args, stat, conn):
    ob = {
        'id': None,
        'tags': {},
        'geo': None,
        'types': [ 'meta' ],
    }

    check_code = \
        pgmapcss.compiler.compile_function_check(stat['statements'], 0, 0, stat) +\
        pgmapcss.compiler.compile_build_result(stat)

    for r in pgmapcss.eval.functions(stat).eval('check_0({})'.format(ob), additional_code=check_code):
        if r[0] == 'result':
            return r[1]['properties']

def get_meta(style_id, args, stat, conn):
    import json
    meta = get_meta_from_code(style_id, args, stat, conn)

    data = {
        'id': style_id,
        'meta': meta,
    }

    open(style_id + '.json', 'w').write(json.dumps(data, indent=2))
    print('Meta information wrote to ' + style_id + '.json')
