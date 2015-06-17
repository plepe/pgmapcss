def init(stat):
    if not 'translation_dir' in stat['config']:
        stat['config']['translation_dir'] = stat['id'] + '.translation'
