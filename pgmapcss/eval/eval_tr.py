class config_eval_tr(config_base):
    mutable = 3

def eval_tr(param):
    if len(param) == 0:
        return ''

    ret = param[0]

    for i, v in enumerate(param[1:]):
        ret = ret.replace("{}", v, 1)
        ret = ret.replace("{%d}" % i, v)

    return ret

# TESTS
# IN ['foobar']
# OUT 'foobar'
# IN ['foo{}', 'bar']
# OUT 'foobar'
# IN ['{}{}', 'foo', 'bar']
# OUT 'foobar'
# IN ['{0}{1}', 'foo', 'bar']
# OUT 'foobar'
# IN ['{1}{0}', 'foo', 'bar']
# OUT 'barfoo'
# IN ['{1}{}', 'foo', 'bar']
# OUT 'barfoo'
# IN []
# OUT ''
