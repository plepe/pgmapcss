class config_eval_push(config_base):
    mutable = 3

def eval_push(param):
    if len(param) == 0:
        return ''

    if len(param) == 1:
        return param[0]

    l = []
    if param[0] != '':
        l = param[0].split(';')

    l.append(param[1])

    return ';'.join(l)

# TESTS
# IN ['pizza;kebab', 'noodles']
# OUT 'pizza;kebab;noodles'
# IN ['', 'pizza']
# OUT 'pizza'
# IN ['pizza', 'kebab']
# OUT 'pizza;kebab'
