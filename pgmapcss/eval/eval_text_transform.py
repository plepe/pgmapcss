def eval_text_transform(param):
    if len(param) == 0:
        return ''

    if len(param) == 1:
        return param[0]

    if param[1] == 'none':
        return param[0]

    elif param[1] == 'uppercase':
        return param[0].upper()

    elif param[1] == 'lowercase':
        return param[0].lower()

    elif param[1] == 'capitalize':
        return param[0].title()

    return param[0]

# TESTS
# IN [ 'fOO bar Bla teST' ]
# OUT 'fOO bar Bla teST'
# IN [ 'fOO bar Bla teST', 'none' ]
# OUT 'fOO bar Bla teST'
# IN [ 'fOO bar Bla teST', 'uppercase' ]
# OUT 'FOO BAR BLA TEST'
# IN [ 'fOO bar Bla teST', 'lowercase' ]
# OUT 'foo bar bla test'
# IN [ 'fOO bar Bla teST', 'capitalize' ]
# OUT 'Foo Bar Bla Test'
# IN [ 'fOO bar Bla teST', 'foobar' ]
# OUT 'fOO bar Bla teST'
