#!/usr/bin/env python3
import sys
import re
import pprint
import pgmapcss.parser
import pgmapcss.compiler
import pgmapcss.version
import pgmapcss.icons
import pgmapcss.symbols
import argparse
import getpass
import pgmapcss.db
import pgmapcss.eval
import os

parser = argparse.ArgumentParser(description='Compiles a MapCSS style description into PostgreSQL functions and builds an accompanying Mapnik stylesheet.')

parser.add_argument('style_id', type=str, help='''\
  style_id is a required argument. The compiled functions will be prefixed
  by 'style_id', e.g. 'pgmapcss_style_id()'. Also the resulting mapnik style
  file will be called style_id.mapnik.
''')

parser.add_argument('-d', '--database', dest='database',
    default=getpass.getuser(),
    help='Name of database (default: username)')

parser.add_argument('--database-type', dest='database_type',
    default='overpass',
    help='Type of database, see doc/database.md for details. (currently supported: overpass (default), osm2pgsql, osmosis)')

parser.add_argument('-u', '--user', dest='user',
    default=getpass.getuser(),
    help='User for database (default: username)')

parser.add_argument('-p', '--password', dest='password',
    default='PASSWORD',
    help='Password for database (default: PASSWORD)')

parser.add_argument('-H', '--host', dest='host',
    default='localhost',
    help='Host for database (default: localhost)')

parser.add_argument('-t', '--template', dest='base_style',
    required=True,
    help='mapcss/renderer base style for the correct renderer and renderer version, e.g. "mapnik-2.0"')

parser.add_argument('--eval-tests', dest='eval_tests', action='store_const',
    const=True, default=False,
    help='Test all eval functions.')

parser.add_argument('-r', '--database-update', dest='database_update',
    default='auto',
    help='Whether the database should be updated to the current version. Possible values: "init": (re-)initializes the database - you need to re-compile all pgmapcss styles, "update": update all database functions, "none": do not update, "auto": if necessary a database functions update will be performed.')

parser.add_argument('-c', '--config', dest='config', nargs='+',
    help='Set configuration options, e.g. -c foo=bar. See doc/config_options.md for available configuration options.')

parser.add_argument('-D', '--defaults', dest='defaults', nargs='+',
    help='Load specified defaults. These can either be included in the pgmapcss distribution (see doc/defaults.md for a list of available defaults) or local files (specified by trailing .mapcss). You may specify several defaults which will be loaded consecutive (e.g. -D josm local.mapcss)')

parser.add_argument('-m', '--mode', dest='mode',
    choices=['database-function', 'standalone'],
    default='database-function',
    help='Mode of execution. Possible values: "database-function" (default): create function in a PostgreSQL database, e.g. for querying by a renderer like Mapnik. "standalone": create a module/executable which returns resp. prints the data.')

parser.add_argument('-P', '--parameters', dest='parameters', nargs='+',
    help='Pass the following parameters as default key-value pairs to the compiled MapCSS code, e.g. "-P foo=bar test=\'Hello World!\'. Only in database-function mode; on standalone mode you can set this at run time.'
)

parser.add_argument('--lang', dest='lang',
    help='Use the given language code (e.g. "en" or "de") for language dependend instruction (e.g. function lang(), text:auto, ...). Default: language from current locale $LANG (or "en").'
)

def main():
    print('pgmapcss version %s' % pgmapcss.version.VERSION)
    args = parser.parse_args()

    style_id = args.style_id

    m = re.match('(.*)\.mapcss$', style_id)
    if m:
        style_id = m.group(1)

    file_name = style_id + '.mapcss'

    parameters = { }
    if args.parameters is not None:
        parameters = {
            p[0:p.find('=')]: p[p.find('=')+1:]
            for p in args.parameters
        }

    if args.lang:
        lang = args.lang
    elif 'lang' in parameters:
        pass
    else:
        lang = os.environ.get('LANG')
        if lang:
            m = re.match('(.*)_', lang)
            if m:
                lang = m.group(1)
        else:
            # default: english
            lang = 'en'

    stat = pgmapcss.compiler.stat._stat({
        'id': style_id,
        'config': {},
        'base_style': args.base_style,
        'icons_dir': style_id + '.icons',
        'global_data': None,
        'mode': args.mode,
        'args': args,
        'lang': lang,
        'parameters': parameters,
    })

    if args.config:
        for v in args.config:
            v = v.split("=")
            if len(v) > 1:
                stat['config'][v[0]] = v[1]
            else:
                stat['config'][v[0]] = True

    conn = pgmapcss.db.connect(args, stat)

    stat['database'] = conn.database

    if not 'unit.srs' in stat['config']:
        stat['config']['unit.srs'] = 900913
    if not 'srs' in stat['config']:
        if stat['mode'] == 'database-function':
            stat['config']['srs'] = 900913
        else:
            stat['config']['srs'] = 4326

    if stat['config'].get('offline', False) in (False, 'false', 'no') and args.database_update in ('init', 're-init'):
        print('* Re-initializing database')
        pgmapcss.db.db_init(conn, stat)

    if stat['config'].get('offline', False) not in (False, 'false', 'no'):
        print('* Using offline mode. Attention! Some functionality might be missing.')

    else:
        db_version = pgmapcss.db.db_version()
        if db_version == None:
            print('* DB functions not installed; installing')
            pgmapcss.db.db_init(conn, stat)
        else:
            db_check = pgmapcss.db.db_version_check()
            if db_check == 1 and args.database_update == 'auto':
                print('* Current DB version: {version} -> updating DB functions'.format(**db_version))
                pgmapcss.db.db_update(conn)

            elif db_check == 2:
                print('* Current DB version: {version}'.format(**db_version))
                print('pgmapcss version too new. Database needs to be re-initialized. Please re-run pgmapcss with parameter "-r init". All Mapnik styles need to be re-compiled afterwards.')
                sys.exit(1)

            elif args.database_update == 'update':
                pgmapcss.db.db_update(conn)

            else:
                print('* Current DB version: {version}'.format(**db_version))

    if args.eval_tests:
        pgmapcss.eval.functions(stat).test_all()
        print('* All tests completed successfully.')

    try:
        os.mkdir(stat['icons_dir'])
    except OSError:
        pass

    eval_functions = pgmapcss.eval.functions(stat).list()

    content = open(file_name).read()

# check if file is XML -> extract MapCSS code
    tree = None
    if re.match('<\?xml', content):
        import xml.dom.minidom as dom
        tree = dom.parse(file_name)
        mapcss = tree.getElementsByTagName("style")
        if mapcss.length != 1:
            print("Require exactly one <style type='text/mapcss'> node")
            sys.exit(1)

        mapcss = mapcss.item(0)
        content = mapcss.firstChild.nodeValue

    try:
        pgmapcss.parser.parse_file(stat, filename=file_name, content=content, base_style=args.base_style, defaults=args.defaults)
    except pgmapcss.parser.ParseError as e:
        print(e)
        sys.exit(1)

    debug = open(style_id + '.output', 'w')

    pp = pprint.PrettyPrinter()

    debug.write("***** Structure of parsed MapCSS style *****\n")
    debug.write(pp.pformat(stat) + '\n')

    pgmapcss.renderer.init(stat)
    pgmapcss.icons.init(stat)
    pgmapcss.symbols.init(stat)

    try:
        style = pgmapcss.compiler.compile_style(stat)
    except pgmapcss.compiler.CompileError as e:
        print(e)
        sys.exit(1)

    #pp.pprint(style)
    for i in style:
        debug.write("\n***** " + i + " *****\n" + style[i])

    if stat['mode'] == 'database-function':
        pgmapcss.db.install(style_id, style, conn)
        pgmapcss.renderer.process_renderer(style_id, args, stat, conn)
    elif stat['mode'] == 'standalone':
        open(style_id + '.py', 'w').write(style['function_match'])
        os.chmod(style_id + '.py', 0o755)
        print('Created executable {}.py'.format(style_id))

    pgmapcss.icons.process_icons(style_id, args, stat, conn)
    pgmapcss.symbols.process_symbols(style_id, args, stat, conn)

    debug.close()

    if 'unresolvable_properties' in stat:
        print('WARNING: Not all values for the following properties could be guessed (e.g. as they are the result of an eval-expression, and therefore some features in the resulting image(s) may be missing: ' + ', '.join(stat['unresolvable_properties']))

    # copy result xml to original dom
    if tree:
        result_tree = dom.parse(style_id + '.mapnik')
        current = result_tree.getElementsByTagName("Map").item(0).firstChild

        while current:
            if re.search('[^\s]', current.toxml()):
                if not re.match('<!\-\-', current.toxml()):
                    copy = dom.parseString(current.toxml())
                    mapcss.parentNode.insertBefore(copy.firstChild, mapcss)
            current = current.nextSibling

        mapcss.parentNode.removeChild(mapcss)
        open(style_id + '.mapnik', 'w').write(tree.toxml())

    print('Debug output wrote to ' + style_id + '.output')
