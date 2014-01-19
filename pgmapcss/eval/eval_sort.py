def eval_sort(param):
    if len(param) == 0:
        return ''

    l = param[0].split(';')

    sorted(l)

    return ';'.join(l)
