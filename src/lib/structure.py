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
Object representation for dmoz structure data

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

from schemes.xml_scheme import DmozStructure as DS
from prepared_statements import *

_log = logging.getLogger(__name__)

class Topic(object):

	def __init__(self, name):
		self.name = unicode(name)
		self.text_vars = {}
		for tvar in DS.text_tags:
			self.text_vars[tvar] = ''
		self.alias = [] #Topic-names
		self.letterbar = [] #Topic-names
		self.related = [] #Topic-names
		self.newsgroups = []
		self.altlangs = {} #Topic-name:lang
		self.symbolic = {} #Topic-name:symbol
		self.attr_by_tag_switch = {DS.ALTLANG : self.set_altlang,
					DS.ALTLANG1 : self.set_altlang,
					DS.LETTERBAR : self.set_letterbar,
					DS.NEWSGROUP : self.set_newsgroup,
					DS.RELATED : self.set_related,
					DS.SYMBOLIC : self.set_symbolic,
					DS.SYMBOLIC1 : self.set_symbolic,
					DS.SYMBOLIC2 : self.set_symbolic,
					}

	def __str__(self):
		return self.name.encode(sys.getdefaultencoding(),'replace')

	def __unicode__(self):
		return self.name

	def __repr__(self):
		return '<Topic ' + self.name + '>'

	@property
	def catid(self):
		return self.text_vars[DS.CATID]

	@property
	def title(self):
		return self.text_vars[DS.TITLE]

	@property
	def lastupdate(self):
		return self.text_vars[DS.LASTUPDATE]

	@property
	def description(self):
		return self.text_vars[DS.DESCRIPTION]

	def save_attr_by_tag(self, tag, attr):
		"""
		Calls the store function corresponding to the given tag
		"""
		#narrow reverses the isfather relation already handeld by
		#DmozPreStructureHandler and is therefore ignored
		if tag in [DS.NARROW, DS.NARROW1, DS.NARROW2]:
			return
		#function calls depending on which attribute is present
		try:
			self.attr_by_tag_switch[tag](attr)
		except KeyError:
			pass

	def set_altlang(self, attr):
		"""
		Adds altlang and resource to self.
		"""
		altlang_res = attr.get(DS.resource_attr)
		altlang, res = altlang_res.split(':')
		self.altlangs[res] = altlang

	def set_letterbar(self, attr):
		"""
		Adds letterbar resources to self.
		"""
		res_name = attr.get(DS.resource_attr)
		self.letterbar.append(res_name)

	def set_newsgroup(self, attr):
		ng_name = attr.get(DS.resource_attr).split(':')[1]
		self.newsgroups.append(ng_name)

	def set_related(self, attr):
		res_name = attr.get(DS.resource_attr)
		self.related.append(res_name)

	def set_symbolic(self, attr):
		symbol_res = attr.get(DS.resource_attr)
		symbol, res = symbol_res.split(':')
		self.symbolic[res] = symbol

	def add_text(self, tag, text):
		self.text_vars[tag] = text

	def add_alias(self, alias):
		self.alias.append(alias)

	def _store_alias(self, engine, conn):
		for alias_name in self.alias:
			alias_dbdata = conn.execute(sel_by_top, tname=alias_name)
			aliascat = alias_dbdata.first()
			if None == aliascat:
				_log.debug('aliascat of {0} not found: {1}'.format(self.name, alias_name))
				continue

			alias_id = aliascat[ct.c.catid]
			try:
				conn.execute(ins_alias, cid=self.catid, alias_cid=alias_id)
			except IntegrityError:
				_log.debug('IntegrityError: Entry <catid({0}) aliascatid({1})> already exists in table "aliases"'.format(self.catid, alias_id))


	def _store_letterbar(self, engine, conn):
		"""
		Sets letterbar=True for every self.letterbar entry.

		conn.execute relies on prepared_statements.py
		"""
		for topic_name in self.letterbar:
			conn.execute(upd_letterbar, tname=topic_name)

	def _store_related(self, engine, conn):
		"""
		Inserts <catid, relcatid> entries into the related table.

		conn.execute relies on prepared_statements.py
		"""
		for rel_top in self.related:
			rtop_dbdata = conn.execute(sel_by_top, tname=rel_top)
			relcat = rtop_dbdata.first()
			if None == relcat:
				_log.debug('relcat of {0} not found: {1}'.format(self.name, rel_top))
				continue

			relcat_id = relcat[ct.c.catid]
			try:
				conn.execute(ins_related, cid=self.catid, rel_cid=relcat_id)
			except IntegrityError:
				_log.debug('IntegrityError: Entry <catid({0}) relcatid({1})> already exists in table "related"'.format(self.catid, relcat_id))

	def _store_newsgroups(self, engine, conn):
		"""
		Inserts <catid, newsgroup> entries into the newsgroups table.

		conn.execute relies on prepared_statements.py
		"""
		for ng in self.newsgroups:
			try:
				conn.execute(ins_newsgroup, cid=self.catid, ngrp=ng)
			except IntegrityError:
				_log.debug('IntegrityError: Entry <catid({0}) newsgroup({1})> already exists in table "newsgroups"'.format(self.catid, ng))

	def _store_altlang(self, engine, conn):
		"""
		Inserts <catid, language, resource> entries into the altlang table.

		conn.execute relies on prepared_statements.py
		"""
		for topic_name, language in self.altlangs.iteritems():
			try:
				conn.execute(ins_altlang, cid=self.catid, lang=language, res=topic_name)
			except IntegrityError:
				_log.debug('IntegrityError: catid({0}) already has an entry for language "{1}"'.format(self.catid, language))


	def _store_symbolics(self, engine, conn):
		"""
		Inserts <catid, symbol, scatid> entries into the symbolics table.

		conn.execute relies on prepared_statements.py
		"""
		for topic_name, symbol in self.symbolic.iteritems():
			top_dbdata = conn.execute(sel_by_top, tname=topic_name)
			symbol_cat = top_dbdata.first()
			if None == symbol_cat:
				_log.debug('symbolic cat of {0} not found: {1}'.format(self.name, topic_name))
				continue

			symbol_cat_id = symbol_cat[ct.c.catid]
			try:
				conn.execute(ins_symbolic, cid=self.catid, symb=symbol, scid=symbol_cat_id)
			except IntegrityError:
				_log.debug('IntegrityError: catid({0}) already has symbol with reference to refcatid({1})'.format(self.catid, symbol_cat_id))


	def _store_lastupdate_and_description(self, engine, conn):
		"""
		Updates <lastupdate> and <description> columns in the category table

		conn.execute relies on prepared_statements.py
		"""
		conn.execute(upd_lup_desc, cid=self.catid, lup=self.text_vars[DS.LASTUPDATE], descr=self.text_vars[DS.DESCRIPTION])

	def store_in_db(self, engine):
		"""
		Stores all attributes in the db.

		Also updates other db entries like the letterbar flag or altlangs
		conn.execute relies on prepared_statements.py
		"""
		conn= engine.connect()

		self._store_alias(engine, conn)
		self._store_letterbar(engine, conn)
		self._store_related(engine, conn)
		self._store_newsgroups(engine, conn)
		self._store_altlang(engine, conn)
		self._store_symbolics(engine, conn)
		self._store_lastupdate_and_description(engine, conn)
