def eval_debug(param):
    if len(param) == 1:
        plpy.notice(param[0])
    else:
        plpy.notice(param)

    return param[0]
