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

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from xml.sax import parse

#the global logger
LOG = logging.Logger('dmoz2db')

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

    if not options.quiet:
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.formatter = logging.Formatter('[%(levelname)s]: %(message)s')
        LOG.addHandler(console)

    if options.log_file:
        log_file_handler = logging.FileHandler(
            options.log_file)
        log_file_handler.setLevel(
            logging.getLevelName(options.log_level))
        log_file_handler.formatter = logging.Formatter(
            '[%(levelname)s]: %(message)s')
        LOG.addHandler(log_file_handler)

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
		engine = create_engine(url)
	except ImportError, i:
		LOG.error('Could not find database driver. Make sure it is installed or specify the driver you want to use in the config file!')
		LOG.error(i)
	return engine

def test_engine(engine):
	"""
	Test if the connection is working
	"""
	try:
		connection = engine.connect()
		connection.close()
		LOG.info('Successfully connected to database')
	except OperationalError, e:
		LOG.error('Could not connect to Database, check your configuration!')
		LOG.error(e)
		sys.exit(DBCONNECT)

if __name__ == '__main__':
	parser = init_optionparser()
	(options, args) = parser.parse_args()
	init_logging(options)

	dbconfig = get_configuration(options.dbconfig)
	engine = new_engine(dbconfig)
	test_engine(engine)
