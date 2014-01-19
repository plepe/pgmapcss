def eval_int(param):
    if len(param) == 0:
        return ''

    try:
        return '%d' % int(param[0])
    except ValueError:
        return ''
