import copy
cache = {}

def merge_options(opt1, opt2):
    ret = copy.deepcopy(opt1)
    for k, v in opt2.items():
        if not k in opt1:
            ret[k] = v
        elif type(v) != type(opt1[k]):
            print('possible_values_merge_options: can\'t merge options of different type ({} vs. {})', type(v), type(opt1[k]))
        elif type(v) == set:
            ret[k] = opt1[k].union(v)
        else:
            print('possible_values_merge_options: can\'t merge options of type {}', type(v))

    return ret


