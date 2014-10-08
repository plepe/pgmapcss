def eval_tag(param):
    for p in param:
        if p in current['tags']:
            v = current['tags'][p]
            if not v is None:
                return v

    return ''

# IN ['name']
# OUT 'Foobar'
# IN ['ref', 'name']
# OUT 'Foobar'
# IN ['ref']
# OUT ''
