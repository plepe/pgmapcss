class config_eval__text_offset(config_base):
    mutable = 0

    def possible_values_all(self, param_values, prop, stat):
# param_values:
# 0 ... text-offset
# 1 ... text-anchor-vertical
# 2 ... icon-image
# 3 ... icon-width
# 4 ... symbol-shape
# 5 ... symbol-size
# 6 ... symbol-stroke-width
        import math
        ret = { 0.0 } # default: no offset

        ret = ret.union(param_values[0]) # text-offset

        # check if maki icon is used - use width values for height
        if len([c for c in param_values[2] if c is not True and not '.' in c]):
            ret = ret.union({ math.ceil(float(w) / 2.0) + 1.0 for w in param_values[3] if w in ("12", "18", "24") }) # icon-width

        # other icons -> read dimensions from global_data
        if 'global_data' in stat and 'icon-image' in stat['global_data']:
            for c in param_values[2]:
                if c in stat['global_data']['icon-image']:
                    d = stat['global_data']['icon-image'][c]
                    ret.add(math.ceil(float(d[1]) / 2.0) + 1.0)

        # symbol-shape used
        if len(param_values[4]):
            ret = ret.union({ math.ceil(float(w) / 2.0) + float(s) + 2.0 for w in param_values[5] for s in param_values[6] })

        ret = { str(int(c)) for c in ret }

        return (ret, 0)

def eval__text_offset(param):
    import math

    prop = current['properties'][current['pseudo_element']]
    if 'text-offset' in prop and prop['text-offset'] is not None:
        return prop['text-offset']

    ret_icon = 0.0
    ret_symbol = 0.0

    if 'icon-image' in prop and prop['icon-image']:
        c = prop['icon-image']
        if c in global_data['icon-image']:
            ret_icon = math.ceil(float(global_data['icon-image'][c][1]) / 2.0) + 1.0

        elif prop['icon-image'][:5] == 'icon:': # maki icon
            ret_icon = math.ceil(float(prop['icon-width']) / 2.0) + 1.0

    if 'symbol-shape' in prop and prop['symbol-shape'] and \
       'symbol-stroke-width' in prop and prop['symbol-stroke-width']:
        ret_symbol = math.ceil(float(prop['symbol-size']) / 2.0) + float(prop['symbol-stroke-width']) + 2.0

    return float_to_str(max(ret_icon, ret_symbol))
