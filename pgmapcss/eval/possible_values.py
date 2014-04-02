import pgmapcss.eval
import pgmapcss
cache = {}

# returns a tuple:
# 1st return value:
#   a set of all possible values; True for unpredictable values
# 2nd return value:
#   mutability of the return value
def possible_values(value, prop, stat):
    global eval_param

    # if we find the value in our cache, we don't need to calculate result
    # only (mutable=3) are added to the cache, we can return 3 as mutability
    # return copy() in case the set gets modified later-on
    if repr(value) in cache:
        return ( cache[repr(value)].copy(), 3 )

    eval_functions = pgmapcss.eval.functions().list()

    if type(value) == str:
        if value[0:2] == 'v:':
            return ( { value[2:] }, 3 )
        elif value[0:2] == 'f:':
            func = value[2:]
            if not func in eval_functions:
                raise Exception('Unknown eval function: ' + func)
            r, mutable = eval_functions[func].possible_values([], prop, stat)
            if type(r) == set:
                return ( r, mutable )
            else:
                return ( { r }, mutable )
        else:
            raise Exception('compiling eval: ' + repr(value))

    if len(value) == 0:
        return {}

    if not value[0][0:2] in ('f:', 'o:'):
        return possible_values(value[0], prop, stat)

    param = [ possible_values(i, prop, stat) for i in value[1:] ]
    mutable = min([ p[1] for p in param ])
    param = [p[0] for p in param ]

    if value[0][0:2] == 'o:':
        func = [ k for k, v in eval_functions.items() if value[0][2:] in v.op ][0]

    elif value[0][0:2] == 'f:':
        func = value[0][2:]

    if not func in eval_functions:
        raise Exception('Unknown eval function: ' + func)

    # make sure all elements are sets
    param = [ {p} if type(p) == str else p for p in param ]

    # some eval functions have a 'possible_values_all' function
    try:
        values, mutable = eval_functions[func].possible_values_all(param, prop, stat)

    # if not, calculate possible values for all combinations of input parameters
    except AttributeError:
        # finally calculate possible results
        result = [
            eval_functions[func].possible_values(p, prop, stat)
            for p in pgmapcss.combinations(param)
        ]
        if(len(result)):
            mutable = min(mutable, min([ r[1] for r in result ]))

        # build a set of all result values
        values = set()
        for r in result:
            values = values.union(r[0] if type(r[0]) == set else { r[0] })

    # if result is static (mutable=3), add a copy of the set to cache
    if mutable == 3:
        cache[repr(value)] = values.copy()

    return ( values, mutable )
