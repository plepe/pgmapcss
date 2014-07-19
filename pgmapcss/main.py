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
    help='mapcss/mapnik base style for the correct mapnik version, e.g. "mapnik-2.0"')

parser.add_argument('--eval-tests', dest='eval_tests', action='store_const',
    const=True, default=False,
    help='Test all eval functions.')

parser.add_argument('-r', '--database-update', dest='database_update',
    default='auto',
    help='Whether the database should be updated to the current version. Possible values: "re-init": re-initializes the database, need to re-compile all pgmapcss styles, "update": update all database functions, "none": do not update, "auto": if necessary a database functions update will be performed.')

parser.add_argument('-o', '--options', dest='options', nargs='+',
    choices=['profiler', 'context'],
    help='Additional options. Currently supported options: "profiler": during execution, show some statistics about query/processing time and count of objects. "context": show bounding box and scale denominator of requests.')

def main():
    print('pgmapcss version %s' % pgmapcss.version.VERSION)
    args = parser.parse_args()

    style_id = args.style_id

    m = re.match('(.*)\.mapcss$', style_id)
    if m:
        style_id = m.group(1)

    file_name = style_id + '.mapcss'

    conn = pgmapcss.db.connect(args)

    if args.database_update == 're-init':
        print('* Re-initializing database')
        pgmapcss.db.db_init(conn)

    db_version = pgmapcss.db.db_version()
    if db_version == None:
        print('* DB functions not installed; installing')
        pgmapcss.db.db_init(conn)
    else:
        db_check = pgmapcss.db.db_version_check()
        if db_check == 1 and args.database_update == 'auto':
            print('* Current DB version: {version} -> updating DB functions'.format(**db_version))
            pgmapcss.db.db_update(conn)

        elif db_check == 2:
            print('* Current DB version: {version}'.format(**db_version))
            print('pgmapcss version too new. Database needs to be re-initialized. Please re-run pgmapcss with parameter "-r re-init". All Mapnik styles need to be re-compiled afterwards.')
            sys.exit(1)

        elif args.database_update == 'update':
            pgmapcss.db.db_update(conn)

        else:
            print('* Current DB version: {version}'.format(**db_version))

    if args.eval_tests:
        pgmapcss.eval.functions().test_all()

    stat = {
        'id': style_id,
        'options': set(args.options) if args.options else set()
    }

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
        pgmapcss.parser.parse_file(stat, filename=file_name, content=content, base_style=args.base_style)
    except pgmapcss.parser.ParseError as e:
        print(e)
        sys.exit(1)

    debug = open(style_id + '.output', 'w')

    pp = pprint.PrettyPrinter()

    debug.write("***** Structure of parsed MapCSS style *****\n")
    debug.write(pp.pformat(stat) + '\n')

    pgmapcss.mapnik.init(stat)
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

    pgmapcss.db.install(style_id, style, conn)
    pgmapcss.mapnik.process_mapnik(style_id, args, stat, conn)
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
