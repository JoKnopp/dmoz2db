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

altlangs_t = Table('altlangs', metadata,
	Column('catid', Integer, ForeignKey('categories.catid')),
	Column('language', Unicode(255)),
	Column('resource', Unicode(255)),
)

categories_t = Table('categories', metadata,
	Column('catid', Integer, primary_key=True, nullable=False),
	Column('Topic', Unicode(512)),
	Column('Title', Unicode(255)),
	Column('Description', Text(65535)),
	Column('lastUpdate', Unicode(255)),
	Column('letterbar', Boolean, default=False),
	Column('fatherid', Integer, ForeignKey('categories.catid'), default=TOPCAT)
)

newsgroups_t = Table('newsgroups', metadata,
	Column('catid', Integer, ForeignKey('categories.catid')),
	Column('newsGroup', Unicode(255)),
)

related_t = Table('related', metadata,
	Column('catid', Integer, ForeignKey('categories.catid')),
	Column('rcatid', Integer, ForeignKey('categories.catid'))
)

symbolics_t = Table('symbolics', metadata,
	Column('catid', Integer, ForeignKey('categories.catid')),
	Column('symbol', Unicode(255)),
	Column('scatid', Integer, ForeignKey('categories.catid'))
)
