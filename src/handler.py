#!/usr/bin/python
# -*- coding: UTF-8 -*-

#TODO update description
"""
Handler for dmoz RDF-like data.
"""

from __future__ import unicode_literals

__version__ = '0.1'
__author__ = 'Johannes Knopp <johannes@informatik.uni-mannheim.de>'
__copyright__ = '© Copyright 2010 Johannes Knopp'

from schemes.xml_scheme import DmozStructure as DS
from xml.sax import handler

from structure import Topic

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
		self.topic = ''
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

class DmozStructureHandler(DmozHandler):
	"""
	handler to parse dmoz structure data into a db
	"""
	
	def __init__(self, db_engine, topic_filter):
		DmozHandler.__init__(self, db_engine, topic_filter)
		self.tags = _get_allowed_tags(DS)
		self.ignore_topic = False
		self.topic = None

	def startElement(self, name, attrs):
		if self.ignore_topic:
			pass
		if name==DS.TOPIC:
			topic = attrs.get(DS.attr_of_name[DS.TOPIC])
			if self.has_topicfilter:
				if not topic.startswith(self.topic_filter):
					self.ignore_topic = True
					return
			self.topic = Topic(topic)

		if name not in self.tags:
			pass

	def endElement(self, name):
		if name==DS.TOPIC:
			self.ignore_topic = False
			self.topic = None

		self.text = ''
