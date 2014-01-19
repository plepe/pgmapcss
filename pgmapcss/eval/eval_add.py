def eval_add(params):
    sum = 0

    for p in params:
        if p == '' or p == None:
            v = 0

        else:
            v = eval_metric(p)

            if v == '':
                return ''

        sum = sum + float(v)

    return sum
