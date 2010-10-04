# Copyright (C) 2010 KenTyde BV
# All rights reserved.
#
# This software is licensed as described in the file LICENSE,
# which you should have received as part of this distribution.

import fix42, util
import couchdb
import copy

class Store(object):
	
	def __init__(self, *args):
		self.db = couchdb.Server(args[0])[args[1]]
		self._last = [0, 0]
	
	@property
	def last(self):
		if self._last != [0, 0]:
			return self._last
		cur = self.db.view('time/in', descending=True, limit=1)
		inc = cur.rows[0].value['MsgSeqNum'] if cur.rows else 0
		cur = self.db.view('time/out', descending=True, limit=1)
		out = cur.rows[0].value['MsgSeqNum'] if cur.rows else 0
		self._last = [inc, out]
		return self._last
	
	def clear(self):
		docs = []
		for row in self.db.view('_all_docs'):
			if row.key.startswith('_design/'):
				continue
			doc = self.db[row.key]
			doc.update({'_deleted': True, '_id': row.key})
			docs.append(doc)
		self.db.update(docs)
	
	def get(self, dir, seq):
		opts = {
			'startkey': [seq, 'z'],
			'endkey': [seq],
			'descending': True,
			'limit': 1,
		}
		cur = self.db.view('seq/%s' % dir, **opts)
		msg = cur.rows[0].value if cur.rows else None
		return msg if msg is None else util.json_decode(msg)
	
	def save(self, dir, msg):
		msg = util.json_encode(msg)
		lkey = {'in': 0, 'out': 1}[dir]
		if self._last[lkey] < msg['MsgSeqNum']:
			self._last[lkey] = msg['MsgSeqNum']
			self.db.update([msg])
