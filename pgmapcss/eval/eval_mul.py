def eval_mul(params):
    ret = 1

    for p in params:
        if p == '' or p == None:
            v = 0

        else:
            v = eval_metric(p)

            if v == '':
                return ''

        ret = ret * float(v)

    return ret
