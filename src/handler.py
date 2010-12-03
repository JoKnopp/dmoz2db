# -*- coding: UTF-8 -*-

#TODO update description
"""
Handler for dmoz RDF-like data.
"""

from __future__ import unicode_literals

__version__ = '0.1'
__author__ = 'Johannes Knopp <johannes@informatik.uni-mannheim.de>'
__copyright__ = '© Copyright 2010 Johannes Knopp'

import re
import logging
import sys

from xml.sax import handler
from sqlalchemy.exc import IntegrityError

import schemes.table_scheme as ts
from schemes.xml_scheme import DmozStructure as DS
from schemes.xml_scheme import DmozContent as DC
from structure import Topic
from content import Link

_log = logging.getLogger(__name__)

def _clean_html(data):
	"""Removes html from a string"""
	p1 = re.compile(r'&lt;.*?&gt;')
	fixed_data = p1.sub('', data)
	p2 = re.compile(r'<.*?>')
	return p2.sub('', fixed_data)

def _get_allowed_tags(scheme_module):
	"""
	Inspects a module to return allowed tags

	Relies on the convention that tag variables are written in uppercase.
	"""
	allowed_tags = set()
	for key in vars(scheme_module).keys():
		if key.isupper():
			allowed_tags.add(vars(scheme_module)[key])
	return allowed_tags

class DmozHandler(handler.ContentHandler): 
	"""
	Base handler to parse dmoz data into a db
	"""

	def __init__(self, db_engine, topic_filter):
		self.engine = db_engine
		if topic_filter != '':
			self.has_topicfilter = True
		else:
			self.has_topicfilter = False
		self.topic_filter = topic_filter
		self.text = ''

	def characters(self, content):
		"""
		Accumulate content

		The content between a xml start and an end tag does not neccessarily
		arrive in one blob. In order to remove html from the text the content
		it is gathered until the end tag shows up.
		"""
		self.text += content.strip()

	def startDocument(self):
		pass

	def endDocument(self):
		pass

class DmozPreStructureHandler(DmozHandler):
	"""
	Insert basic Topic information into a database

	Basic information consists of the topic name, title and catid
	"""

	def __init__(self, db_engine, topic_filter):
		DmozHandler.__init__(self, db_engine, topic_filter)
		self.topic_count = 0
		self.ignore_topic = False
		self.topic_name = ''
		self.topic_title = ''

	def startElement(self, name, attrs):
		if self.ignore_topic:
			pass
		if name==DS.TOPIC:
			self.topic_count += 1
			topic = attrs.get(DS.topic_attr)
			if self.has_topicfilter:
				if not topic.startswith(self.topic_filter):
					self.ignore_topic = True
					return
			self.topic_name = topic
			title = topic.split('/')[-1]
			if not title:
				title = ''
			self.topic_title = title

	def endElement(self, tagname):
		if (tagname==DS.TOPIC):
			if self.topic_count % 10000 == 0:
				sys.stdout.write('.')
				if self.topic_count % 200000 == 0:
					sys.stdout.write('\b - {0} Topics parsed \n'.format(self.topic_count))
				sys.stdout.flush()
			self.ignore_topic = False
			self.topic_name = ''
		elif tagname == (DS.CATID) and (self.topic_name != ''):
			catid = int(self.text)
			insertion = ts.categories_t.insert(values={
									'catid':catid,
									'Topic':self.topic_name,
									'Title':self.topic_title
										}
									)
			try:
				self.engine.execute(insertion)
			except IntegrityError, e:
				_log.debug(e)
				pass
			self.ignore_topic = True

		elif tagname == DS.RDF:
			print
			_log.info('Parsed {0} Topics'.format(self.topic_count))

		#cf. character function of DmozHandler
		self.text = ''

class DmozStructureHandler(DmozHandler):
	"""
	Insert additional topic information to a database
	"""
	
	def __init__(self, db_engine, topic_filter):
		DmozHandler.__init__(self, db_engine, topic_filter)
		self.topic_count = 0
		self.allowed_tags = _get_allowed_tags(DS)
		self.ignore_topic = False
		self.topic = None

	def startElement(self, name, attrs):
		if self.ignore_topic:
			pass
		if name==DS.TOPIC:
			if self.topic != None:
				#Store self.topic at startElement because aliases are added to
				#it between </topic> and <topic>
				self.topic.store_in_db(self.engine)
			self.topic_count += 1
			topic = attrs.get(DS.topic_attr)
			if self.has_topicfilter:
				if not topic.startswith(self.topic_filter):
					self.ignore_topic = True
					self.topic = None
					return
			self.topic = Topic(topic)

		elif (name==DS.ALIAS) and (self.topic != None):
			title_alias = attrs.get(DS.topic_attr)
			alias = title_alias.split(':')[-1]
			self.topic.add_alias(alias)

		elif name not in self.allowed_tags:
			_log.debug('Found forbidden tag "{0}"'.format(name))
			pass

		#save attrs in self.topic
		elif (self.topic) and (name not in DS.text_tags):
			self.topic.save_attr_by_tag(name, attrs)

	def endElement(self, tagname):
		if tagname==DS.TOPIC:
			if self.topic_count % 10000 == 0:
				sys.stdout.write('.')
				if self.topic_count % 200000 == 0:
					sys.stdout.write('\b - {0} Topics parsed \n'.format(self.topic_count))
				sys.stdout.flush()
			self.ignore_topic = False

		elif tagname == DS.RDF:
			print
			_log.info('Parsed {0} Topics'.format(self.topic_count))

		elif self.ignore_topic:
			return

		elif (tagname in DS.text_tags) and (self.topic != None):
			text = _clean_html(self.text)
			self.topic.add_text(tagname, text)

		#cf. character function of DmozHandler
		self.text = ''


class DmozContentHandler(DmozHandler):
	"""
	Insert links related to a topic to a database
	"""
	def __init__(self, db_engine, topic_filter):
		DmozHandler.__init__(self, db_engine, topic_filter)
		self.topic_count = 0
		self.allowed_tags = _get_allowed_tags(DC)
		self.ignore_topic = False
		self.link = None
	
	def startElement(self, name, attrs):
		if name==DC.TOPIC:
			self.topic_count += 1
			topic = attrs.get(DS.topic_attr)
			if self.has_topicfilter:
				if not topic.startswith(self.topic_filter):
					self.ignore_topic = True
					return
				else:
					self.ignore_topic = False
					return

		if self.ignore_topic:
			pass

		elif name==DC.EXTERNALPAGE:
			self.link = Link(attrs.get(DC.ext_attr), self.catid)

		elif name not in self.allowed_tags:
			_log.debug('Found forbidden tag "{0}"'.format(name))
			pass

	def endElement(self, tagname):
		if tagname==DC.TOPIC:
			if self.topic_count % 10000 == 0:
				sys.stdout.write('.')
				if self.topic_count % 200000 == 0:
					sys.stdout.write('\b - {0} Topics parsed \n'.format(self.topic_count))
				sys.stdout.flush()

		elif tagname == DS.RDF:
			print
			_log.info('Parsed {0} Topics'.format(self.topic_count))

		elif self.ignore_topic:
			return

		#save text fields
		elif tagname == DC.CATID:
			self.catid = self.text
		elif tagname == DC.TITLE:
			self.link.title = self.text
		elif tagname == DC.DESCRIPTION:
			self.link.description = self.text

		elif tagname == DC.EXTERNALPAGE:
			self.link.store_in_db(self.engine)
			self.link = None

		#cf. character function of DmozHandler
		self.text = ''
