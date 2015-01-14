class config_eval_length(config_base):
    mutable = 3

def eval_length(param, current):
    if len(param) == 0:
        return ''

    return str(len(param[0]))

# TESTS
# IN ['restaurant;bar']
# OUT '14'
# IN ['restaurant']
# OUT '10'
# IN ['']
# OUT '0'
