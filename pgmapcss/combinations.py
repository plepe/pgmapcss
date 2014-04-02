def combinations(src):
    combinations = [[]]
    for p in src:
        new_combinations = []
        for combination in combinations:
            for v in p:
                c = list(combination) # copy original list
                c.append(v)
                new_combinations.append(c)
        combinations = new_combinations

    return combinations
