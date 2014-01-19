def eval_power(param):
    if len(param) < 2:
        return ''

    f1 = eval_metric(param[0:1])
    f2 = eval_metric(param[1:2])

    f1 = float(f1) if f1 != '' else 0.0
    f2 = float(f2) if f2 != '' else 0.0

    return '%G' % (f1 ** f2)
