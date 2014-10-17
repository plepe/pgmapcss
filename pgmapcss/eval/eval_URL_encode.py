class config_eval_URL_encode(config_base):
    mutable = 3

def eval_URL_encode(param, current):
    if len(param) == 0:
        return ''

    import urllib.parse
    return urllib.parse.quote(param[0])

# TESTS
# IN [ 'test/' ]
# OUT 'test/'
# IN [ 'El Niño' ]
# OUT 'El%20Ni%C3%B1o'
