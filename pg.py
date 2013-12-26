import pghstore

def format(value):
    add_quotes = False
    esc_quotes = True

    if type(value) == str:
        value = value
        add_quotes = True

    elif type(value) == int or \
         type(value) == float:
        value = repr(value)

    elif type(value) == dict:
        value = pghstore.dumps(value)
        add_quotes = True

    elif type(value) == list:
        value = 'Array[' + ','.join([format(i) for i in value]) + ']'
        esc_quotes = False

    else:
        raise Exception('pg.format(): ' + str(type(value)) + ' not supported')

    if esc_quotes:
        value = value.replace("'", "''")

    if add_quotes:
        value = "'" + value + "'"

    return value
