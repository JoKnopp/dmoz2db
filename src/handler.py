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

from xml.sax import handler
from sqlalchemy.exc import IntegrityError

import schemes.table_scheme as ts
from schemes.xml_scheme import DmozStructure as DS
from structure import Topic

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
				_log.info('Parsed {0} Topics'.format(self.topic_count))
			self.ignore_topic = False
			self.topic_name = ''
		elif tagname == DS.CATID and self.topic_name != '':
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
			self.topic_count += 1
			topic = attrs.get(DS.topic_attr)
			if self.has_topicfilter:
				if not topic.startswith(self.topic_filter):
					self.ignore_topic = True
					return
			self.topic = Topic(topic)

		elif name not in self.allowed_tags:
			_log.debug('Found forbidden tag {0}'.format(name))
			pass

		#save attrs in self.topic
		elif (self.topic) and (name not in DS.text_tags):
			self.topic.save_attr_by_tag(name, attrs)

	def endElement(self, tagname):
		if tagname==DS.TOPIC:
			if self.topic_count % 10000 == 0:
				_log.info('Parsed {0} Topics'.format(self.topic_count))
			self.ignore_topic = False
			if self.topic != None:
				self.topic.store_in_db(self.engine)
				self.topic = None
		elif (tagname in DS.text_tags) and (self.topic != None):
			text = _clean_html(self.text)
			self.topic.add_text(tagname, text)

		#cf. character function of DmozHandler
		self.text = ''
