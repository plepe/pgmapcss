def eval_tag(param):
    for p in param:
        if p in current['tags']:
            return current['tags'][p]

    return ''

# IN ['name']
# OUT 'Foobar'
# IN ['ref', 'name']
# OUT 'Foobar'
