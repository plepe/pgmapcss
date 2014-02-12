def eval_substr(param):
    if len(param) == 0:
        return ''

    if len(param) == 1:
        return param[0]

    if param[0] is None:
        return ''

    start = to_int(param[1])

    if start is None:
        return ''
    elif start > len(param[0]):
        return ''
    elif start < 0:
        start = len(param[0]) + start
        if start < 0:
            start = 0

    if len(param) == 2:
        length = len(param[0])
    else:
        length = to_int(param[2])
        if length is None:
            return ''

        if length < 0:
            length = len(param[0]) + length
            if length < start:
                return ''

        else:
            length = start + length

    return param[0][start:length]

# TESTS
# IN [ '1234567890' ]
# OUT '1234567890'
# IN [ '1234567890', '1' ]
# OUT '234567890'
# IN [ '1234567890', '1', '2' ]
# OUT '23'
# IN [ '1234567890', '4' ]
# OUT '567890'
# IN [ '1234567890', '4', '2' ]
# OUT '56'
# IN [ '1234567890', '6', '6' ]
# OUT '7890'
# IN [ '1234567890', '-2' ]
# OUT '90'
# IN [ '1234567890', '-2', '0' ]
# OUT ''
# IN [ '1234567890', '-4', '2' ]
# OUT '78'
# IN [ '1234567890', '-4', '20' ]
# OUT '7890'
# IN [ '1234567890', '2', '-2' ]
# OUT '345678'
# IN [ '1234567890', '-6', '-2' ]
# OUT '5678'
# IN [ '1234567890', '-6', '-6' ]
# OUT ''
# IN [ '1234567890', '-6', '-10' ]
# OUT ''
# IN [ '1234567890', '-20' ]
# OUT '1234567890'
# IN [ '1234567890', '-20', '2' ]
# OUT '12'
# IN [ '1234567890', 'foo' ]
# OUT ''
# IN [ '1234567890', '1', 'foo' ]
# OUT ''
