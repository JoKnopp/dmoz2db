#!/usr/bin/python
# -*- coding: UTF-8 -*-

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
from xml.sax import parse

from sqlalchemy import create_engine, Index
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql.expression import bindparam

from schemes import table_scheme

#the global logger
LOG = logging.Logger(__name__, level=logging.DEBUG)
#the database logger
DBLOG = logging.getLogger('sqlalchemy')
DBLOG.setLevel(logging.DEBUG)

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
        default=os.path.expanduser('~/data/dmoz/structure.rdf.u8'),
        help='Specify the dmoz structure file [default: %default]'
    )

    parser.add_option('-c', '--content-file',
        type='string',
        dest='content_file',
        default=os.path.expanduser('~/data/dmoz/content.rdf.u8'),
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

    if not options.quiet:
        loglevel = logging.INFO
        console = logging.StreamHandler()
        if options.debug:
            loglevel = logging.DEBUG
        console.setLevel(loglevel)
        console.formatter = logging.Formatter('[%(levelname)s]: %(message)s')
        LOG.addHandler(console)
        DBLOG.addHandler(console)

    if options.log_file:
        log_file_handler = logging.FileHandler(
            options.log_file)
        log_file_handler.setLevel(
            logging.getLevelName(options.log_level))
        log_file_handler.formatter = logging.Formatter(
            '[%(levelname)s]: %(message)s')
        LOG.addHandler(log_file_handler)
        DBLOG.addHandler(log_file_handler)

    LOG.debug('Logging initialised')
    DBLOG.debug('DB logging initialised')

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
        engine = create_engine(url, encoding='utf-8')
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

def create_index(engine):
    LOG.info('creating index for topics')
    i = Index('topics', table_scheme.categories_t.c.Topic)
    i.create(engine)
    LOG.info('done')


def add_father_ids(engine):
    ct = table_scheme.categories_t
    connection = engine.connect()

    #prepared statements
    selection = ct.select().where(ct.c.Topic==bindparam('f_topic'))
    fid_update = ct.update().where(ct.c.catid==bindparam('child_id')).values(fatherid=bindparam('fatherid_'))
    all_categories = connection.execute('SELECT * FROM categories')

    LOG.info('Generating father ids...This may take some time, so have a cup
    of tea!')
    counter = 0
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
            LOG.warning('Found no father for "{0}", searched for "{1}"'.format(topic, father_topic))
            continue
        father_id = father[ct.c.catid]
        connection.execute(fid_update, child_id=catid, fatherid_=father_id)
        if counter % 10000 == 0:
            LOG.info(counter)
    LOG.info('Father ids generated')
    

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
        parse(xmlstream, structure_prehandler)

    create_index(engine)
    add_father_ids(engine)


