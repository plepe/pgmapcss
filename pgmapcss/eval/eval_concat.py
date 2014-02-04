def eval_concat(param):
    ret = ''
    for p in param:
        ret += p or ''

    return ret

# TESTS
# IN ['foo', 'bar']
# OUT 'foobar'
