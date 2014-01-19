def eval_set(param):
    if len(param) < 3:
        return ''

    i = int(param[1])
    if i == '':
        return param[0]

    l = param[0].split(';')

    l[i] = param[2]

    return ';'.join(l)
