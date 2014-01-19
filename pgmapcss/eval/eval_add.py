def eval_add(params):
    ret = 0

    for p in params:
        v = eval_metric([p])

        if v == '':
            return ''

        ret = ret + float(v)

    return '%G' % ret

# TESTS
# IN ['1', '']
# OUT ''
# IN ['1.5', '2']
# OUT '3.5'
# IN ['1', '2']
# OUT '3'
# IN ['-2', '2']
# OUT '0'
# IN ['1', '2', '3']
# OUT '6'
