def load_translation(translation_dir, abs_path):
    import json
    global translation_strings
    translation_strings = {}

    try:
        data = open(translation_dir + '/' + parameters['lang'] + '.json', 'r', encoding='utf-8').read()
    except IOError:
        try:
            data = open(abs_path + '/' + translation_dir + '/' + parameters['lang'] + '.json', 'r', encoding='utf-8').read()
        except IOError:
            return

    translation_strings = json.loads(data)
