def strip_includes(stream, stat):
    import re
    ret = ''
    selectors = set()
    else_selectors = set()
    include = True

    while True:
        r = stream.readline()
        if not r:
            return ret
        r = r.decode('utf-8')

        m = re.match('# (START|ELSE|END) (.*)', r)
        if m:
            if m.group(1) == 'END':
                if m.group(2) in selectors:
                    selectors.remove(m.group(2))
                if m.group(2) in else_selectors:
                    else_selectors.remove(m.group(2))
            elif m.group(1) == 'START':
                selectors.add(m.group(2))
                if m.group(2) in else_selectors:
                    else_selectors.remove(m.group(2))
            elif m.group(1) == 'ELSE':
                else_selectors.add(m.group(2))
                if m.group(2) in selectors:
                    selectors.remove(m.group(2))

            include = not len({
                True
                for s in selectors
                if not s in stat['config'] or stat['config'][s] in ('false', False, 'no')
            }) + len({
                True
                for s in else_selectors
                if s in stat['config'] and stat['config'][s] not in ('false', False, 'no')
            })

        elif include:
            ret += r

    return ret
