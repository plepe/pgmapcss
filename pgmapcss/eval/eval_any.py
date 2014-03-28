class config_eval_any(config_base):
    mutable = 3

    def possible_values(self, param_values, prop, stat):
        ret = set()

        for p in param_values:
            if p is not None and p != '':
                ret.add(p)

                if p is not True:
                    return ( ret, 3 )

        return ( ret, 3 )

def eval_any(param):
    for p in param:
        if p is not None and p != '':
            return p

    return ''

# TESTS
# IN ['foo', 'bar']
# OUT 'foo'
# IN ['', 'bar']
# OUT 'bar'
# IN ['', '', '']
# OUT ''
# IN []
# OUT ''
