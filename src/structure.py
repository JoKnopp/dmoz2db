#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Object representation for dmoz structure data
"""

from __future__ import unicode_literals

__version__ = '0.1'
__author__ = 'Johannes Knopp <johannes@informatik.uni-mannheim.de>'
__copyright__ = '© Copyright 2010 Johannes Knopp'

from schemes.xml_scheme import DmozStructure as DS

import sys

class Topic(object):

	def __init__(self, name):
		self.name = unicode(name)
		self.text_vars = {}
		for tvar in DS.text_tags:
			self.text_vars[tvar] = ''
		self.letterbar = False
		self.narrow = [] #Topic-objects
		self.related = [] #Topic-objects
		self.newsgroups = []
		self.altlangs = {} #lang:Topic-object
		self.symbolic = {} #topic:Topic-object
		self.attr_by_tag_switch = {DS.ALTLANG : self.set_altlang,
					DS.ALTLANG1 : self.set_altlang,
					DS.LETTERBAR : self.set_letterbar,
					DS.NARROW : self.append_narrow_link,
					DS.NARROW1 : self.append_narrow_link,
					DS.NARROW2 : self.append_narrow_link,
					DS.NEWSGROUP : self.set_newsgroup,
					DS.RELATED : self.set_related,
					DS.SYMBOLIC : self.set_symbolic,
					DS.SYMBOLIC1 : self.set_symbolic,
					DS.SYMBOLIC2 : self.set_symbolic,
					}

	def __str__(self):
		return self.name.encode(sys.getdefaultencoding(),'replace')

	def __unicode__(self):
		return self.name

	def __repr__(self):
		return '<Topic ' + self.name + '>'

	@property
	def catid(self):
		return self.text_vars[DS.CATID]

	@property
	def title(self):
		return self.text_vars[DS.TITLE]

	@property
	def lastupdate(self):
		return self.text_vars[DS.LASTUPDATE]

	@property
	def description(self):
		return self.text_vars[DS.DESCRIPTION]

	def save_attr_by_tag(self, tag, attr):
		#function calls depending on which attribute is present
		try:
			self.attr_by_tag_switch[tag](attr)
		except KeyError:
			pass

	def set_altlang(self, attr):
		"""
		Adds altlang and resource to self.
		"""
		altlang_res = attr.get(DS.resource_attr)
		altlang, res = altlang_res.split(':')
		self.altlangs[altlang] = Topic(res)

	def set_letterbar(self, attr):
		"""
		Returns a new Topic object from letterbar attribute.

		Also adds a narrow link to self
		"""
		res_name = attr.get(DS.resource_attr)
		new_topic = Topic(res_name)
		new_topic.letterbar = True
		#letterbar is a narrow link
		self.narrow.append(new_topic)

	def append_narrow_link(self, attr):
		res_name = attr.get(DS.resource_attr)
		new_topic = Topic(res_name)
		self.narrow.append(new_topic)

	def set_newsgroup(self, attr):
		ng_name = attr.get(DS.resource_attr).split(':')[1]
		self.newsgroups.append(ng_name)

	def set_related(self, attr):
		res_name = attr.get(DS.resource_attr)
		new_topic = Topic(res_name)
		self.add_related_link(new_topic)

	def set_symbolic(self, attr):
		symboltopic_res = attr.get(DS.resource_attr)
		topic, res = symboltopic_res.split(':')
		self.symbolic[topic] = Topic(res)

	def add_related_link(self, topic_obj):
		assert type(topic_obj) == Topic
		self.related.append(topic_obj)

	def add_text(self, tag, text):
		self.text_vars[tag] = text
