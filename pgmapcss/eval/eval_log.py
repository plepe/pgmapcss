class config_eval_log(config_base):
    mutable = 3

def eval_log(param, current):
    if len(param) == 0:
        return ''

    try:
        v = float(param[0])
    except ValueError:
        return ''

    if v <= 0:
        return ''

    try:
        base = float(param[1])
    except IndexError:
        base = None
    except ValueError:
        return ''

    if base is not None and base <= 0:
        return ''

    if base:
        return float_to_str(math.log(v, base))
    else:
        return float_to_str(math.log(v))

# TESTS
# IN ['1']
# OUT '0'
# IN ['4', '2']
# OUT '2'
# IN ['4']
# OUT '1.3862943611198906'
# IN ['foo']
# OUT ''
# IN ['10;100']
# OUT ''
# IN ['0']
# OUT ''
# IN ['-1']
# OUT ''
# IN ['2', '0']
# OUT ''
