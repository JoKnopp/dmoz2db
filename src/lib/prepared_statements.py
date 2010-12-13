# -*- coding: UTF-8 -*

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
Prepared sqlalchemy statements make your life easier and your code more
readable
"""

from __future__ import unicode_literals
from __future__ import absolute_import

__version__ = '0.1'
__author__ = 'Johannes Knopp <johannes@informatik.uni-mannheim.de>'
__copyright__ = '© Copyright 2010 Johannes Knopp'

from sqlalchemy.sql.expression import bindparam

from .schemes import table_scheme as ts

at = ts.aliases_t
ct = ts.categories_t
rt = ts.related_t
ngt = ts.newsgroups_t
alt = ts.altlangs_t
st = ts.symbolics_t
xpt = ts.externalpages_t

#selects
sel_by_id = ct.select().where(
        ct.c.catid==bindparam('cid',required=True))
sel_by_top = ct.select().where(
        ct.c.Topic==bindparam('tname',required=True))

#updates
upd_letterbar = ct.update().where(
        ct.c.Topic==bindparam('tname',required=True)
    ).values(letterbar=True)
upd_lup_desc = ct.update().where(
        ct.c.catid==bindparam('cid',required=True)
    ).values(
        lastupdate=bindparam('lup',required=True)
    ).values(
        Description=bindparam('descr',required=True)
    )

#inserts
ins_alias = at.insert().values(
        catid=bindparam('cid', required=True)
    ).values(
        alias_catid=bindparam('alias_cid', required=True)
    )
ins_related = rt.insert().values(
        catid=bindparam('cid',required=True)
    ).values(
        rcatid=bindparam('rel_cid',required=True)
    )
ins_newsgroup = ngt.insert().values(
        catid=bindparam('cid',required=True)
    ).values(
        newsgroup=bindparam('ngrp',required=True)
    )
ins_altlang = alt.insert().values(
        catid=bindparam('cid',required=True)
    ).values(
        language=bindparam('lang',required=True)
    ).values(
        resource=bindparam('res',required=True)
    )
ins_symbolic = st.insert().values(
        catid=bindparam('cid',required=True)
    ).values(
        scatid=bindparam('scid',required=True)
    ).values(
        symbol=bindparam('symb',required=True)
    )
ins_externalpage = xpt.insert().values(
        catid=bindparam('cid',required=True)
    ).values(
        link=bindparam('lnk',required=True)
    ).values(
        Title=bindparam('lnktitle',required=True)
    ).values(
        Description=bindparam('descr',required=True)
    )
