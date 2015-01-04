class config_eval_keys_of_tags(config_base):
    mutable = 0

def eval_keys_of_tags(param):
    return ';'.join(current['tags'])

# IN []
# OUT_SET 'cuisine;amenity;name:en;name;name:de'
