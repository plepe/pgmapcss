def eval_num(param):
    if len(param) == 0:
        return ''

    try:
        value = float(param[0])
    except ValueError:
        return ''

    return '%G' % value
