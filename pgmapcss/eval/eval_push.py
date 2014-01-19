def eval_push(param):
    if len(param) == 0:
        return ''

    if len(param) == 1:
        return param[0]

    l = param[0].split(';')

    l.append(param[1])

    return ';'.join(l)
