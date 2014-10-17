class config_eval_switch(config_base):
    mutable = 3

    def possible_values_all(self, param_values, prop, stat):
        check = param_values[0]
        ret = set()
        done = set()

        for i in range(1, len(param_values) - 1, 2):
            if True in param_values[i]:
                done.add(True)
                ret = ret.union(param_values[i + 1])

            else:
                p = {
                    b
                    for a in param_values[i]
                    for b in a.split(";")
                }
                done = done.union(p)

                if True in check or len([
                    c
                    for a in param_values[i]
                    for b in a.split(";")
                    for c in check
                    if b == c
                ]):
                    ret = ret.union(param_values[i + 1])

        if len(param_values) % 2 == 0:
            p = param_values[-1]
        else:
            p = { '' }

        if True in check or len([
            True
            for c in check
            if not c in done
        ]):
            ret = ret.union(p)

        return ( ret, 3 )

def eval_switch(param, current):
    if len(param) == 0:
        return ''

    value = param[0]

    for i in range(1, len(param) - 1, 2):
        comp_values = param[i].split(';')

        if value in comp_values:
            return param[i + 1]

    if len(param) % 2 == 0:
        return param[-1]

    return ''

# TESTS
# IN ['5', '1', 'foo', '5', 'bar']
# OUT 'bar'
# IN ['4', '1', 'foo', '5', 'bar']
# OUT ''
# IN ['4', '1', 'foo', '4;5', 'bar']
# OUT 'bar'
# IN ['4', '1', 'foo', '5', 'bar', 'else']
# OUT 'else'
# IN ['4', '1', 'foo', '4', 'bar', 'else']
# OUT 'bar'
# IN ['else', '1', 'foo', '5', '4', 'else']
# OUT 'else'
# IN ['4', 'else']
# OUT 'else'
