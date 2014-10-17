class config_eval_keys_of_tags(config_base):
    mutable = 0

def eval_keys_of_tags(param, current):
    return ';'.join(current['tags'])

# IN []
# OUT 'cuisine;amenity;name'
