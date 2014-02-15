def to_color(value):
    if re.match('#[a-fA-F0-9]{6,8}', value):
        return value

    return None
