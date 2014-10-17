class config_eval_set(config_base):
    mutable = 3

def eval_set(param, current):
    if len(param) < 3:
        return ''

    i = eval_int([param[1]], current)
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
