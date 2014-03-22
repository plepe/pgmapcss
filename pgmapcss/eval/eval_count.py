class config_eval_count(config_base):
    mutable = 3

def eval_count(param):
    if len(param) == 0:
        return ''

    if param[0] == '':
        return '0'

    l = param[0].split(';')

    return str(len(l))

# TESTS
# IN ['restaurant;bar']
# OUT '2'
# IN ['restaurant']
# OUT '1'
# IN ['']
# OUT '0'
