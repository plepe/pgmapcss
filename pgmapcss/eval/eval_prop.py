def eval_prop(param):
    if len(param) == 0:
        return ''

    pseudo_element = current['pseudo_element']

    if len(param) > 1:
        pseudo_element = param[1]

    if pseudo_element not in current['properties']:
        return ''

    if param[0] in current['properties'][pseudo_element]:
        return current['properties'][pseudo_element][param[0]]
    else:
        return ''

# TESTS
# IN ['width']
# OUT '2'
# IN ['width', 'test']
# OUT ''
# IN ['fill-color', 'test']
# OUT '#00ff00'
# IN ['width', 'foobar']
# OUT ''
