def compile_pseudo_class_condition(condition, stat):
    if condition['key'] in ('active', 'hover'):
        return 'False'

    else:
        print('unknown/unsupported pseudo class: {key}'.format(**condition))
        return 'False'
