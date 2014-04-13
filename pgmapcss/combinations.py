def combinations(src):
    '''Takes a list or dict of sets and returns all possible combinations, e.g.:
INPUT [{'a', 'b'}, {'x', 'y'}]
OUTPUT [['a', 'y'], ['a', 'x'], ['b', 'y'], ['b', 'x']]

INPUT {'key1': {'a', 'b'}, 'key2': {'x', 'y'}}
OUTPUT [{'key1': 'a', 'key2': 'y'}, {'key1': 'b', 'key2': 'y'}, {'key1': 'a', 'key2': 'y'}, {'key1': 'b', 'key2': 'x'}]

'''
    if type(src) == list:
        combinations = [[]]
        for p in src:
            new_combinations = []
            for combination in combinations:
                for v in p:
                    c = list(combination) # copy original list
                    c.append(v)
                    new_combinations.append(c)
            combinations = new_combinations

    elif type(src) == dict:
        combinations = [{}]
        for k, p in src.items():
            new_combinations = []
            for combination in combinations:
                for v in p:
                    c = dict(combination) # copy original list
                    c[k] = v
                    new_combinations.append(c)
            combinations = new_combinations

    return combinations
