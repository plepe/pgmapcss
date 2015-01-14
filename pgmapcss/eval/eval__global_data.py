class config_eval__global_data(config_base):
    mutable = 1

    def possible_values(self, param_values, prop, stat):
        v = stat['global_data']

        if v is None:
            return (True, 1)

        for k in param_values:
            if type(v) in (set, list, tuple):
                try:
                    k = int(k)
                except ValueError:
                    return ('', 1)

                if k >= len(v):
                    return ('', 1)

            elif not k in v:
                return ('', 1)

            v = v[k]

        return (str(v), 1)

def eval__global_data(param, current):
    v = global_data

    for k in param:
        if type(v) in (set, list, tuple):
            try:
                k = int(k)
            except ValueError:
                return ''

            if k >= len(v):
                return ''

        elif not k in v:
            return ''

        v = v[k]

    return str(v)
