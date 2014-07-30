class config_eval_replace(config_base):
    mutable = 3

def eval_replace(param):
    if len(param) == 0:
        return ''

    if len(param) < 3:
        return param[0]

    return param[0].replace(param[1], param[2])

# TESTS
# IN [ 'foobar', 'o', 'a' ]
# OUT 'faabar'
# IN [ 'Hello OSM', 'OSM', 'OpenStreetMap' ]
# OUT 'Hello OpenStreetMap'
