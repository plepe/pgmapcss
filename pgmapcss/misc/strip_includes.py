def strip_includes(stream, stat):
    import re
    ret = ''
    selectors = set()
    include = True

    while True:
        r = stream.readline()
        if not r:
            return ret
        r = r.decode('utf-8')

        m = re.match('# (START|END) (.*)', r)
        if m:
            if m.group(1) == 'END':
                selectors.remove(m.group(2))
            elif m.group(1) == 'START':
                selectors.add(m.group(2))

            include = not len({
                True
                for s in selectors
                if (not s in stat['config'] or stat['config'][s] in ('false', False, 'no')) and (not s in stat['options'])
            })

        if include:
            ret += r

    return ret
