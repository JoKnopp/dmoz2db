# -*- coding: UTF-8 -*

"""
Object representation for dmoz structure data

Able to store its contents in a database
"""

from __future__ import unicode_literals

__version__ = '0.1'
__author__ = 'Johannes Knopp <johannes@informatik.uni-mannheim.de>'
__copyright__ = '© Copyright 2010 Johannes Knopp'

from sqlalchemy.sql.expression import bindparam

import schemes.table_scheme as ts

at = ts.aliases_t
ct = ts.categories_t
rt = ts.related_t
ngt = ts.newsgroups_t
alt = ts.altlangs_t
st = ts.symbolics_t

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
