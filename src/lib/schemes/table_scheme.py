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
Table descriptions for dmoz data

Created on Nov 22nd 2010
"""

from sqlalchemy import *

__version__ = '0.1'
__author__ = 'Johannes Knopp <johannes@informatik.uni-mannheim.de>'
__copyright__ = '© Copyright 2010 Johannes Knopp'

metadata = MetaData()
TOPCAT = 1 #catid for "" - Used as default ref if real catid is unknown

#structure.rdf
aliases_t = Table('aliases', metadata,
	Column('catid', Integer, ForeignKey('categories.catid'), primary_key=True),
	Column('alias_catid', Integer, ForeignKey('categories.catid'), primary_key=True)
)

altlangs_t = Table('altlangs', metadata,
	Column('catid', Integer, ForeignKey('categories.catid'), primary_key=True),
	Column('language', Unicode(255), primary_key=True),
	Column('resource', Unicode(512))
)
Index('idx_resource', altlangs_t.c.resource, mysql_length=110)

categories_t = Table('categories', metadata,
	Column('catid', Integer, primary_key=True, nullable=False),
	Column('Topic', Unicode(512)),
	Column('Title', Unicode(255), index=True),
	Column('Description', Text(65535)),
	Column('lastupdate', Unicode(255)),
	Column('letterbar', Boolean, default=False),
	Column('fatherid', Integer, ForeignKey('categories.catid'), default=TOPCAT)
)
Index('idx_topic', categories_t.c.Topic, mysql_length=125)

newsgroups_t = Table('newsgroups', metadata,
	Column('catid', Integer, ForeignKey('categories.catid'), primary_key=True),
	Column('newsgroup', Unicode(255), primary_key=True)
)

related_t = Table('related', metadata,
	Column('catid', Integer, ForeignKey('categories.catid'), primary_key=True),
	Column('rcatid', Integer, ForeignKey('categories.catid'), primary_key=True)
)

symbolics_t = Table('symbolics', metadata,
	Column('catid', Integer, ForeignKey('categories.catid'), primary_key=True),
	Column('symbol', Unicode(255)),
	Column('scatid', Integer, ForeignKey('categories.catid'), primary_key=True)
)

#content.rdf
externalpages_t = Table('externalpages', metadata,
	Column('catid', Integer, ForeignKey('categories.catid')),
	Column('link', Unicode(650)),
	Column('Title', Unicode(255), index=True),
	Column('Description', Text(65535))
)
Index('idx_link', externalpages_t.c.link, mysql_length=60)
