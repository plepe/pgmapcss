def eval_count(param):
    if len(param) == 0:
        return ''

    l = param[0].split(';')

    return str(len(l))

# TESTS
# IN ['restaurant;bar']
# OUT '2'
