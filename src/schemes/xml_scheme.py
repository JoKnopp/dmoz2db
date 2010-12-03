# -*- coding: UTF-8 -*-

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
Classes for the dmoz XML-Tags

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
	RDF = 'RDF'
	SYMBOLIC = 'symbolic'
	SYMBOLIC1 = 'symbolic1'
	SYMBOLIC2 = 'symbolic2'

	#attributes
	topic_attr = 'r:id'
	resource_attr = 'r:resource'

	text_tags = set()
	for tag in [CATID,TITLE,LASTUPDATE,DESCRIPTION]:
		text_tags.add(tag)

class DmozContent():
	EXTERNALPAGE = 'ExternalPage'
	TOPIC = 'Topic'
	AGES = 'ages'
	ATOM = 'atom'
	CATID = 'catid'
	DESCRIPTION = 'd:Description'
	TITLE = 'd:Title'
	LINK = 'link'
	LINK1 = 'link1'
	MEDIADATE = 'mediadate'
	PDF = 'pdf'
	PDF1 = 'pdf1'
	PRIORITY = 'priority'
	RDF = 'RDF'
	RSS = 'rss'
	RSS1 = 'rss1'
	TOPIC2 = 'topic'
	TYPE = 'type'
	UKSITE = 'uksite'

	topic_attr = 'r:id'
	ext_attr = 'about'

	text_tags = set()
	for tag in [CATID,TITLE,DESCRIPTION]:
		text_tags.add(tag)
