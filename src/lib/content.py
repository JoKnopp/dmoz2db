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
Object representation for dmoz content data

Able to store its contents in a database
"""

from __future__ import unicode_literals

__version__ = '0.1'
__author__ = 'Johannes Knopp <johannes@informatik.uni-mannheim.de>'
__copyright__ = '© Copyright 2010 Johannes Knopp'

import sys
import logging

from sqlalchemy.sql.expression import bindparam
from sqlalchemy.exc import IntegrityError

from prepared_statements import *

_log = logging.getLogger(__name__)

class Link(object):

    def __init__(self, link, catid):
        self.catid = catid
        self.link = link
        self.title = ''
        self.description = ''

    def __str__(self):
        return self.__unicode__.encode('utf8')

    def __unicode__(self):
        return self.link

    def store_in_db(self, engine):
        """
        Inserts the values into the externalpage Table
        """
        conn = engine.connect()

        try:
            conn.execute(ins_externalpage,
                        cid=self.catid,
                        lnk=self.link,
                        lnktitle=self.title,
                        descr=self.description
                        )
        except IntegrityError:
            _log.debug('IntegrityError: catid({0}) already has link({1})'.format(self.catid, self.link))
