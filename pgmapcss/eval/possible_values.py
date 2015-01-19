import pgmapcss.eval
import pgmapcss
from .merge_options import merge_options
cache = {}

# returns a tuple:
# 1st return value:
#   a set of all possible values; True for unpredictable values
# 2nd return value:
#   mutability of the return value
# 3rd return value:
#   additional eval options, e.g. requirements
def possible_values(value, prop, stat):
    global eval_param
    eval_options = {}

    # if we find the value in our cache, we don't need to calculate result
    # only (mutable=3) are added to the cache, we can return 3 as mutability
    # return copy() in case the set gets modified later-on
    if repr(value) in cache:
        return ( cache[repr(value)].copy(), 3, {} )

    eval_functions = pgmapcss.eval.functions().list()

    if type(value) == str:
        if value[0:2] == 'v:':
            return ( { value[2:] }, 3, {} )
        elif value[0:2] == 'f:':
            func = value[2:]
            if not func in eval_functions:
                if func in pgmapcss.eval.functions().aliases:
                    func = pgmapcss.eval.functions().aliases[func]
                else:
                    raise Exception('Unknown eval function: ' + func)
            result = eval_functions[func].possible_values([], prop, stat)
            values = result[0]
            mutable = result[1]
            if len(result) > 2:
                eval_options = merge_options(eval_options, result[2])

            if type(values) == set:
                return ( values, mutable, eval_options )
            else:
                return ( { values }, mutable, eval_options )
        else:
            raise Exception('compiling eval: ' + repr(value))

    if len(value) == 0:
        return {}

    if not value[0][0:2] in ('f:', 'o:', 'u:'):
        return possible_values(value[0], prop, stat)

    result = [ possible_values(i, prop, stat) for i in value[1:] ]
    mutable = min([ p[1] for p in result ])
    for r in result:
        if len(r) > 2:
            eval_options = merge_options(eval_options, r[2])
    param = [p[0] for p in result ]

    if value[0][0:2] == 'o:':
        func = [ k for k, v in eval_functions.items() if value[0][2:] in v.op and not v.unary ][0]

    if value[0][0:2] == 'u:':
        func = [ k for k, v in eval_functions.items() if value[0][2:] in v.op and v.unary ][0]

    elif value[0][0:2] == 'f:':
        func = value[0][2:]

    if not func in eval_functions:
        if func in pgmapcss.eval.functions().aliases:
            func = pgmapcss.eval.functions().aliases[func]
        else:
            raise Exception('Unknown eval function: ' + func)

    # make sure all elements are sets
    param = [ {p} if type(p) == str else p for p in param ]

    # some eval functions have a 'possible_values_all' function
    try:
        r = eval_functions[func].possible_values_all(param, prop, stat)
        values = r[0]
        m = r[1]
        if len(r) > 2:
            eval_options = merge_options(eval_options, r[2])
        mutable = min(mutable, r[1])

    # if not, calculate possible values for all combinations of input parameters
    except AttributeError:
        combinations = pgmapcss.combinations(param)

        if len(combinations) > 256:
            print('eval::possible_values: found {} possible combinations for "{}" using function {}() -> stopping getting possible values'.format(len(combinations), prop.get('key', 'unknown'), func))
            return ({ True }, mutable, eval_options)

        # finally calculate possible results
        result = [
            eval_functions[func].possible_values(p, prop, stat)
            for p in combinations
        ]
        if(len(result)):
            mutable = min(mutable, min([ r[1] for r in result ]))
            for r in result:
                if len(r) > 2:
                    eval_options = merge_options(eval_options, r[2])

        # build a set of all result values
        values = set()
        for r in result:
            values = values.union(r[0] if type(r[0]) == set else { r[0] })

    # if result is static (mutable=3), add a copy of the set to cache
    if mutable == 3:
        cache[repr(value)] = values.copy()

    return ( values, mutable, eval_options )
