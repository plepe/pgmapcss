def color_values(value):
    # not a valid color
    if not re.match('#[0-9a-fA-F]{6,8}', param[0]):
        return None

    # get the color values for each channel
    return [
        int(value[i*2+1:i*2+3], 16)
        for i in range(0, int((len(value) - 1) / 2))
    ]
