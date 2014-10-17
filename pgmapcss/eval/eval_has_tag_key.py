class config_eval_has_tag_key(config_base):
    mutable = 1

def eval_has_tag_key(param, current):
    if len(param) == 0:
        return ''
    if param[0] in current['tags']:
        return 'true'

    return 'false'

# IN ['name']
# OUT 'true'
# IN ['ref']
# OUT 'false'
