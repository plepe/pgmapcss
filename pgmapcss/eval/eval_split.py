def eval_split(param):
    if len(param) < 2:
        return ''

    l = param[0].split(param[1])

    return ';'.join(l)
