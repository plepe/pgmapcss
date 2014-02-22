_includes = {}

def register_includes(inc):
    global _includes
    _includes = dict(list(_includes.items()) + list(inc.items()))

def include_text():
    global _includes
    ret = ''
    for name, function in _includes.items():
        ret += function

    return ret

def includes():
    global _includes
    print(_includes)
    return _includes
