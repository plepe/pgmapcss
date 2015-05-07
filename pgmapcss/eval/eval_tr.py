class config_eval_tr(config_base):
    mutable = 0
    def possible_values_all(self, param_values, prop, stat):
        if not 'translation_strings' in stat:
            stat['translation_strings'] = set()
        stat['translation_strings'] |= param_values[0]
        return ( { True }, 0 )


def eval_tr(param):
    if len(param) == 0:
        return ''

    ret = param[0]

    for i, v in enumerate(param):
        for j, w in enumerate(current['condition-keys']):
            if w is not None:
                param[i] = param[i].replace("{" + str(j) + ".key}", w)
                param[i] = param[i].replace("{" + str(j) + ".value}", current['tags'][w] if w in current['tags'] else '')
                param[i] = param[i].replace("{" + str(j) + ".tag}", w + '=' + current['tags'][w] if w in current['tags'] else '')

    for i, v in enumerate(param[1:]):
        ret = ret.replace("{}", v, 1)
        ret = ret.replace("{%d}" % i, v)

    return ret

# TESTS
# IN ['foobar']
# OUT 'foobar'
# IN ['foo{}', 'bar']
# OUT 'foobar'
# IN ['{}{}', 'foo', 'bar']
# OUT 'foobar'
# IN ['{0}{1}', 'foo', 'bar']
# OUT 'foobar'
# IN ['{1}{0}', 'foo', 'bar']
# OUT 'barfoo'
# IN ['{1}{}', 'foo', 'bar']
# OUT 'barfoo'
# IN ['{} {} {}', '{0.key}', '{0.value}', '{0.tag}']
# OUT 'amenity restaurant amenity=restaurant'
# IN []
# OUT ''
