def load_translation(id):
    global translation_strings
    translation_strings = {}

    try:
        data = open(id + '.translation/' + parameters['lang'] + '.json', 'r').read()
    except IOError:
        return

    translation_strings = json.loads(data)
