class config_eval_number_of_tags(config_base):
    mutable = 0

def eval_number_of_tags(param):
    return str(len(current['tags']))

# IN []
# OUT '5'
