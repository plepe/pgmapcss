import os
import json

def create_template(stat):
    if not 'translation_strings' in stat or len(stat['translation_strings']) == 0:
        return

    # generate translation files
    try:
        os.mkdir(stat['config']['translation_dir'])
    except OSError:
        pass

    translation_strings = {}
    if 'translation_update' in stat['config'] and stat['config']['translation_update']:
        try:
            translation_strings = open(stat['config']['translation_dir'] + '/template.json', 'r').read()
            translation_strings = json.loads(translation_strings)
        except IOError:
            pass

    for k in stat['translation_strings']:
        translation_strings[k] = ''

    open(stat['config']['translation_dir'] + '/template.json', 'w').write(json.dumps(translation_strings, sort_keys=True, indent=4, ensure_ascii=False))
