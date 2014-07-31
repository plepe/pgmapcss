class config_eval_regexp_test(config_base):
    mutable = 3

def eval_regexp_test(param):
    if len(param) < 2:
        return ''

    f = 0
    if len(param) > 2:
        if 'i' in param[2]:
            f = f | re.IGNORECASE

    m = re.search(param[0], param[1], flags=f)

    if not m:
        return 'false'

    return 'true'

# TESTS
# IN ['oo', 'foobar']
# OUT 'true'
# IN ['aa', 'foobar']
# OUT 'false'
# IN ['OO', 'foobar']
# OUT 'false'
# IN ['OO', 'foobar', 'i']
# OUT 'true'
# IN ['\\/', 'foo/bar']
# OUT 'true'
# IN ['^(.*)gasse$', 'Beingasse']
# OUT 'true'
