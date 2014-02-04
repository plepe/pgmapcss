def eval_area(param):
    if len(param) == 0:
        return ''

    plan = plpy.prepare('select ST_Area($1) as area', ['geometry'])
    res = plpy.execute(plan, param)

    zoom = eval_metric(['1u'])

    if zoom == '':
        return ''

    ret = res[0]['area'] * float(zoom) ** 2

    return float_to_str(ret)

# TESTS
# IN ['010300002031BF0D000100000004000000AE47E1BA1F52354185EB51B83EAE5641C3F528DC1F5235413D0AD7D33FAE5641295C8F4224523541000000B03EAE5641AE47E1BA1F52354185EB51B83EAE5641']
# OUT '1.7576717461588458'
