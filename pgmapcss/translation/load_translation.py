def load_translation(id, abs_path):
    import json
    global translation_strings
    translation_strings = {}

    try:
        data = open(id + '.translation/' + parameters['lang'] + '.json', 'r').read()
    except IOError:
        try:
            data = open(abs_path + '/' + id + '.translation/' + parameters['lang'] + '.json', 'r').read()
        except IOError:
            return

    translation_strings = json.loads(data)
