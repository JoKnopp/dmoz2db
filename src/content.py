# -*- coding: UTF-8 -*-

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
from sqlalchemy.exceptions import IntegrityError

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
