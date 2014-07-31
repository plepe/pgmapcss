class config_eval_regexp_match(config_base):
    mutable = 3

def eval_regexp_match(param):
    if len(param) < 2:
        return ''

    f = 0
    if len(param) > 2:
        if 'i' in param[2]:
            f = f | re.IGNORECASE

    m = re.search(param[0], param[1], flags=f)

    if not m:
        return ''

    ret = [ m.group(0) ]
    for r in m.groups():
        ret.append(r)

    return ';'.join(ret)

# TESTS
# IN ['oo', 'foobar']
# OUT 'oo'
# IN ['aa', 'foobar']
# OUT ''
# IN ['OO', 'foobar']
# OUT ''
# IN ['OO', 'foobar', 'i']
# OUT 'oo'
# IN ['\\/', 'foo/bar']
# OUT '/'
# IN ['^(.*)(gasse)$', 'Beingasse']
# OUT 'Beingasse;Bein;gasse'
