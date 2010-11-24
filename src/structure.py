#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Object representation for dmoz structure data
"""

from __future__ import unicode_literals

__version__ = '0.1'
__author__ = 'Johannes Knopp <johannes@informatik.uni-mannheim.de>'
__copyright__ = '© Copyright 2010 Johannes Knopp'

class Topic(object):
	
	def __init__(self, name):
		self.name = name
		self.catid = -1
		self.title = ''
		self.lastupdate = ''
		self.description = ''
		self.narrow = []
		self.related = []
		self.altlang = {} #lang:path
		self.symbolic = {} #topic:path

	def __repr__(self):
		return 'Topic(' + self.name + ')'
