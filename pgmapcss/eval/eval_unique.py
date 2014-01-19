def eval_unique(param):
    if len(param) == 0:
        return ''

    if len(param) == 1:
        param = param[0].split(';')

    return ';'.join(set(param))
