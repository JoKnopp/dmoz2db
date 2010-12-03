# -*- coding: UTF-8 -*-
#!/usr/bin/python

#This file is part of dmoz2db.

#dmoz2db is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#dmoz2db is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with dmoz2db.  If not, see <http://www.gnu.org/licenses/>.

"""
dmoz2db

Database importer for dmoz RDF-like data.
"""
from __future__ import unicode_literals

__version__ = '0.1'
__author__ = 'Johannes Knopp <johannes@informatik.uni-mannheim.de>'
__copyright__ = '© Copyright 2010 Johannes Knopp'

import os
import sys
import optparse
import logging
import ConfigParser #for the database config file
import handler
import time
from datetime import timedelta
from xml.sax import parse

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql.expression import bindparam

from schemes import table_scheme

#the global logger
LOG = logging.Logger(__name__)
LOG.setLevel(logging.DEBUG)
#the database logger
DBLOG = logging.getLogger('sqlalchemy')
DBLOG.setLevel(logging.DEBUG)
#the parser logger
PARSELOG = logging.getLogger('handler')
PARSELOG.setLevel(logging.DEBUG)
#structure
SLOG = logging.getLogger('structure')
SLOG.setLevel(logging.DEBUG)


#exit status
#Error while connecting to the database
DBCONNECT = 2

def init_optionparser():
    """Initialise command line parser."""

    usage = 'Usage: %prog [options]'

    parser = optparse.OptionParser(usage)

    parser.add_option('--db', '--dbconfig',
        type='string',
        dest='dbconfig',
        default='db.conf',
        help='Config file for the db connection'
    )

    parser.add_option('-q', '--quiet',
        action='store_true',
        dest='quiet',
        default=False,
        help='Ignore informal output'
    )

    parser.add_option('-s', '--structure-file',
        type='string',
        dest='structure_file',
        default=os.path.expanduser('structure.rdf.u8'),
        help='Specify the dmoz structure file [default: %default]'
    )

    parser.add_option('-c', '--content-file',
        type='string',
        dest='content_file',
        default=os.path.expanduser('content.rdf.u8'),
        help='Specify the dmoz content file [default: %default]'
    )

    parser.add_option('-t', '--topic-filter',
        type='string',
        dest='topic_filter',
        default='',
        help='Specify the most general category which should be filtered for [default: %default]'
        )

    parser.add_option('-k', '--keep-db',
        default=False,
        action='store_true',
        dest='keep_db',
        help='Do not delete existing tables [default: %default]'
        )

    parser.add_option('-d', '--debug',
        default=False,
        action='store_true',
        dest='debug',
        help='Print debug output [default: %default]'
        )

    #Logging related options
    log_options = optparse.OptionGroup(parser,
            'Logging',
            'Specify log file handling.'
    )

    log_level = ['DEBUG', 'INFO', 'WARNING', 'ERROR']

    log_options.add_option('--log-file',
                            metavar='FILE',
                            type='string',
                            help='write logs to FILE'
                            )

    log_options.add_option('--log-file-level',
                            help='set log level (' +
                            ', '.join(log_level) +
                            ') [default: %default]',
                            action='store', default='INFO',
                            type='choice', choices=log_level
                            )

    parser.add_option_group(log_options)
    return parser

def init_logging(options):
    """Initialise logging framework

    :param options: Options obtained from optparse"""

    error = logging.StreamHandler(sys.stderr)
    error.setLevel(logging.ERROR)
    error.formatter = logging.Formatter('[%(levelname)s]: %(message)s')
    LOG.addHandler(error)
    DBLOG.addHandler(error)
    SLOG.addHandler(error)
    PARSELOG.addHandler(error)

    if not options.quiet:
        loglevel = logging.INFO
        dbloglevel = logging.WARNING
        db_console = logging.StreamHandler()
        console = logging.StreamHandler()
        if options.debug:
            loglevel = logging.DEBUG
            dbloglevel = logging.INFO
        console.setLevel(loglevel)
        console.formatter = logging.Formatter('[%(levelname)s]: %(message)s')
        db_console.setLevel(dbloglevel)
        db_console.formatter = logging.Formatter('[%(levelname)s]: %(message)s')
        LOG.addHandler(console)
        PARSELOG.addHandler(console)
        SLOG.addHandler(console)
        DBLOG.addHandler(db_console)

    if options.log_file:
        log_file_handler = logging.FileHandler(
            options.log_file)
        log_file_handler.setLevel(
            logging.getLevelName(options.log_level))
        log_file_handler.formatter = logging.Formatter(
            '[%(levelname)s]: %(message)s')
        LOG.addHandler(log_file_handler)
        PARSELOG.addHandler(log_file_handler)
        SLOG.addHandler(log_file_handler)
        DBLOG.addHandler(log_file_handler)

    LOG.debug('Logging initialised')

def get_configuration(config_filename):
    new_config = ConfigParser.SafeConfigParser()
    try:
        with open(config_filename, 'r') as dbconf_file:
            new_config.readfp(dbconf_file)
    except ConfigParser.ParsingError, parse_err:
        LOG.error('Could not parse configuration file: %s'%(
            config_filename))
    else:
        LOG.info('Reading configuration from: %s'%(config_filename))
    return new_config

def new_engine(cf):
    """
    Creates an engine from the config cf

    :param cf: data from ConfigParser
    """
    try:
        dialect = cf.get('Database', 'type')
        user = cf.get('Database', 'db_user')
        pw = cf.get('Database', 'password')
        host = cf.get('Database', 'host')
        db_name = cf.get('Database', 'dbname')
        port = cf.get('Database', 'port')
        driver = cf.get('Database', 'driver')
    except ConfigParser.NoOptionError, importantInfoMissing:
        try: #every necessary information present?
            assert(dialect)
            assert(user)
            assert(pw)
            assert(host)
            assert(db_name)
            try:
                assert(port)
            except NameError, portNotFound:
                LOG.info('Missing port configuration. Trying to connect with default values.')
                port = ''
            try:
                assert(driver)
            except NameError, driverNotFound:
                LOG.info('Missing driver configuration. Trying to connect with default values.')
                driver = ''

        except AssertionError:
            LOG.error('Database connection information incomplete!')
            LOG.error(importantInfoMissing)
            sys.exit(DBCONNECT)

    if driver:
        driver = '+' + driver
    if port:
        port = ':' + port
    url = dialect + driver + '://' + user + ':' + pw + '@' + host + port + '/' + db_name
    try:
        engine = create_engine(url + '?charset=utf8', encoding='utf-8')
    except ImportError, i:
        LOG.error('Could not find database driver. Make sure it is installed or specify the driver you want to use in the config file!')
        LOG.error(i)
    return engine

def test_engine(engine):
    """
    Tests if the connection is working
    """
    try:
        connection = engine.connect()
        connection.close()
        LOG.info('Successfully connected to database')
    except OperationalError, e:
        LOG.error('Could not connect to Database, check your configuration!')
        LOG.error(e)
        sys.exit(DBCONNECT)

def setup_db(engine, keep_db):
    """
    Clears and initialises tables
    """
    if not keep_db:
        LOG.info('Dropping existing tables')
        table_scheme.metadata.drop_all(engine)
    LOG.info('Initialising tables')
    table_scheme.metadata.create_all(engine)

def add_father_ids(engine):
    ct = table_scheme.categories_t
    connection = engine.connect()

    #prepared statements
    selection = ct.select().where(ct.c.Topic==bindparam('f_topic'))
    fid_update = ct.update().where(ct.c.catid==bindparam('child_id')).values(fatherid=bindparam('fatherid_'))
    all_categories = connection.execute('SELECT * FROM categories')

    counter = 0
    sys.stdout.write('\n')
    for row in all_categories:
        counter += 1
        topic = row.Topic
        title = row.Title
        catid = row.catid
        if catid < 3: #ignore "" and "Top"
            continue

        index = len(topic)-(len(title)+1)
        father_topic = topic[:index]

        father_selection = connection.execute(selection, f_topic=father_topic)
        father = father_selection.first()
        if father == None:
            LOG.debug('Found no father for "{0}", searched for "{1}"'.format(topic, father_topic))
            continue
        father_id = father[ct.c.catid]
        connection.execute(fid_update, child_id=catid, fatherid_=father_id)
        if counter % 10000 == 0:
            sys.stdout.write('.')
            if counter % 200000 == 0:
                sys.stdout.write('\b - {0} ids generated\n'.format(counter))
            sys.stdout.flush()
    print
    

if __name__ == '__main__':
    parser = init_optionparser()
    (options, args) = parser.parse_args()
    init_logging(options)

    dbconfig = get_configuration(options.dbconfig)
    engine = new_engine(dbconfig)
    test_engine(engine)
    setup_db(engine, options.keep_db)

    structure_prehandler = handler.DmozPreStructureHandler(engine, options.topic_filter)
    with open(options.structure_file, 'r') as xmlstream:
        LOG.info('Starting first parse of {0}'.format(options.structure_file))
        firstparse_starttime = time.time()
        parse(xmlstream, structure_prehandler)
        firstparse_duration = timedelta(seconds=(time.time()-firstparse_starttime))
        LOG.info('done - added all Topics to the database (took {0})'.format(firstparse_duration))

    LOG.info('Generating father ids')
    idgen_starttime = time.time()
    add_father_ids(engine)
    idgen_duration = timedelta(seconds=(time.time()-idgen_starttime))
    LOG.info('Father id generation successful (took {0})'.format(idgen_duration))

    structure_handler = handler.DmozStructureHandler(engine, options.topic_filter)

    with open(options.structure_file, 'r') as xmlstream:
        LOG.info('Starting second parse of {0}'.format(options.structure_file))
        secondparse_starttime = time.time()
        parse(xmlstream, structure_handler)
        secondparse_duration = timedelta(seconds=(time.time()-secondparse_starttime))
        LOG.info('done - inserted additional topic-information to the database (took {0})'.format(secondparse_duration))

    content_handler = handler.DmozContentHandler(engine, options.topic_filter)

    with open(options.content_file, 'r') as xmlstream:
        LOG.info('Starting parse of {0}'.format(options.content_file))
        contentparse_starttime = time.time()
        parse(xmlstream, content_handler)
        contentparse_duration = timedelta(seconds=(time.time()-contentparse_starttime))
        LOG.info('done - inserted externalpage information to the database (took {0})'.format(contentparse_duration))

        full_duration = firstparse_duration + idgen_duration + secondparse_duration + contentparse_duration
        LOG.info('Import complete in {0}'.format(full_duration))
