#!/usr/bin/env python3
import sys
import re
import pprint
import pgmapcss.parser
import pgmapcss.compiler
import argparse
import getpass
import pgmapcss.db
import os

parser = argparse.ArgumentParser(description='Compiles a MapCSS style description into PostgreSQL functions and builds an accompanying Mapnik stylesheet.')

parser.add_argument('style_id', type=str, help='''\
  style_id is a required argument. The compiled functions will be prefixed
  by 'style_id', e.g. 'style_id_match()'. Also the resulting mapnik style file
  will be called style_id.mapnik.
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

def main():
    args = parser.parse_args()

    style_id = args.style_id
    file_name = style_id + '.mapcss'

    conn = pgmapcss.db.connect(args)

    pgmapcss.db.init_db(conn)

    stat = {}

    try:
        pgmapcss.parser.parse_file(stat, file=file_name, base_style=args.base_style)
    except pgmapcss.parser.ParseError as e:
        print(e)
        sys.exit(1)

    pp = pprint.PrettyPrinter()
    pp.pprint(stat)

    style = pgmapcss.compiler.compile_style(style_id, stat)

    #pp.pprint(style)
    for i in style:
        print("***** " + i + " *****\n" + style[i])

    pgmapcss.db.install(style_id, style, conn)
    pgmapcss.mapnik.process_mapnik(style_id, args, stat, conn)
