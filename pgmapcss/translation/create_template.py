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

    translation_strings = {
        k: ''
        for k in stat['translation_strings']
    }

    open(stat['config']['translation_dir'] + '/template.json', 'w').write(json.dumps(translation_strings, sort_keys=True, indent=2))


