def eval_set(param):
    if len(param) < 3:
        return ''

    i = eval_int([param[1]])
    if i == '':
        return param[0]
    i = int(i)

    l = param[0].split(';')

    l[i] = param[2]

    return ';'.join(l)

# TESTS
# IN ['pizza;kebab;noodles', '2', 'burger']
# OUT 'pizza;kebab;burger'
# IN ['pizza;kebab;noodles', '0', 'burger']
# OUT 'burger;kebab;noodles'
