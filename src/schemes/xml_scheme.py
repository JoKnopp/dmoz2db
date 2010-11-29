# -*- coding: UTF-8 -*-
"""Classes for the dmoz XML-Tags

The class cover the tags of structure.rdf.u8 and content.rdf.u8

Created on Nov 22nd 2010
"""

from __future__ import unicode_literals

__version__ = '0.1'
__author__ = 'Johannes Knopp <johannes@informatik.uni-mannheim.de>'
__copyright__ = '© Copyright 2010 Johannes Knopp'

class DmozStructure():
	ALIAS = 'Alias'
	TARGET = 'Target'
	TOPIC = 'Topic'
	ALTLANG = 'altlang'
	ALTLANG1 = 'altlang1'
	CATID = 'catid'
	DESCRIPTION = 'd:Description'
	TITLE = 'd:Title'
	EDITOR = 'editor'
	LASTUPDATE = 'lastUpdate'
	LETTERBAR = 'letterbar'
	NARROW = 'narrow'
	NARROW1 = 'narrow1'
	NARROW2 = 'narrow2'
	NEWSGROUP = 'newsgroup'
	RELATED = 'related'
	SYMBOLIC = 'symbolic'
	SYMBOLIC1 = 'symbolic1'
	SYMBOLIC2 = 'symbolic2'

	#attributes
	topic_attr = 'r:id'
	resource_attr = 'r:resource'

	text_tags = set()
	for tag in [CATID,TITLE,LASTUPDATE,DESCRIPTION]:
		text_tags.add(tag)
