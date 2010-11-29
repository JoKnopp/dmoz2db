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
