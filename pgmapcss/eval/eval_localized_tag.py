def eval_localized_tag(param):
    if len(param) == 0:
        return ''
    p = param[0]

    if len(param) > 1:
        p1 = p + ':' + param[1]
    else:
        p1 = p + ':' + parameters['lang']

    if p1 in current['tags']:
        v = current['tags'][p1]
        if not v is None:
            return v

    if p in current['tags']:
        v = current['tags'][p]
        if not v is None:
            return v

    return ''

# IN ['name']
# OUT 'English Foobar'
# IN ['name', 'fr']
# OUT 'Foobar'

