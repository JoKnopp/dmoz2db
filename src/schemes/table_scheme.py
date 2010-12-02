# -*- coding: UTF-8 -*-
"""Table descriptions for dmoz data

Created on Nov 22nd 2010
"""

from sqlalchemy import *

__version__ = '0.1'
__author__ = 'Johannes Knopp <johannes@informatik.uni-mannheim.de>'
__copyright__ = '© Copyright 2010 Johannes Knopp'

metadata = MetaData()
TOPCAT = 1 #catid for "" - Used as default ref if real catid is unknown

aliases_t = Table('aliases', metadata,
	Column('catid', Integer, ForeignKey('categories.catid'), primary_key=True),
	Column('alias_catid', Integer, ForeignKey('categories.catid'), primary_key=True)
)

altlangs_t = Table('altlangs', metadata,
	Column('catid', Integer, ForeignKey('categories.catid'), primary_key=True),
	Column('language', Unicode(255), primary_key=True),
	Column('resource', Unicode(512), index=True),
)

categories_t = Table('categories', metadata,
	Column('catid', Integer, primary_key=True, nullable=False),
	Column('Topic', Unicode(512), index=True),
	Column('Title', Unicode(255), index=True),
	Column('Description', Text(65535)),
	Column('lastupdate', Unicode(255)),
	Column('letterbar', Boolean, default=False),
	Column('fatherid', Integer, ForeignKey('categories.catid'), default=TOPCAT)
)

newsgroups_t = Table('newsgroups', metadata,
	Column('catid', Integer, ForeignKey('categories.catid'), primary_key=True),
	Column('newsgroup', Unicode(255), primary_key=True),
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
