class config_eval_osm_id(config_base):
    mutable = 1

def eval_osm_id(param, current):
    return current['object']['id']

# TESTS
# IN []
# OUT 'n123'
