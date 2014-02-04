def eval_any(param):
    for p in param:
        if p is not None and p != '':
            return p

    return ''

# TESTS
# IN ['foo', 'bar']
# OUT 'foo'
# IN ['', 'bar']
# OUT 'bar'
# IN ['', '', '']
# OUT ''
# IN []
# OUT ''
