includes = {}

def register_includes(inc):
    global includes
    includes = dict(list(includes.items()) + list(inc.items()))

def include_text():
    global includes
    ret = ''
    for name, function in includes.items():
        ret += function

    return ret
