from datetime import datetime, date

import fix42
import couchdb
import copy

def ddecode(s):
	return datetime.strptime(s, '%Y-%m-%d %H:%M:%S').date()

def dtdecode(s):
	return datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

TYPES = {
	date: (str, ddecode),
	datetime: (lambda s: str(s)[:19], dtdecode),
}

class Store(object):
	
	def __init__(self, *args):
		self.db = couchdb.Server(args[0])[args[1]]
		self._last = None
	
	@property
	def last(self):
		if self._last is not None:
			return self._last
		cur = self.db.view('seq/in', descending=True, limit=1)
		inc = cur.rows[0].key if cur.rows else 0
		cur = self.db.view('seq/out', descending=True, limit=1)
		out = cur.rows[0].key if cur.rows else 0
		self._last = [inc, out]
		return self._last
	
	def _encode(self, msg):
		msg = copy.copy(msg)
		for k, v in msg.iteritems():
			
			if k in fix42.REPEAT:
				msg[k] = [self._encode(i) for i in v]
			
			codec = TYPES.get(fix42.WTAGS[k][1])
			if codec is not None:
				msg[k] = codec[0](v)
			
		return msg
	
	def _decode(self, msg):
		new = {}
		for k, v in msg.iteritems():
			
			if k.startswith('_'):
				continue
			
			if k in fix42.REPEAT:
				msg[k] = [self._decode(i) for i in v]
			
			codec = TYPES.get(fix42.WTAGS[k][1])
			new[k] = v
			if codec is not None:
				new[k] = codec[1](v)
		
		return new
	
	def get(self, dir, seq):
		msg = self.db.get('%s-%s' % (dir, seq))
		return msg if msg is None else self._decode(msg)
	
	def save(self, dir, msg):
		
		msg = self._encode(msg)
		msg['_id'] = '%s-%s' % (dir, msg['MsgSeqNum'])
		
		lkey = {'in': 0, 'out': 1}[dir]
		if self._last[lkey] < msg['MsgSeqNum']:
			self._last[lkey] = msg['MsgSeqNum']
		
		if msg['_id'] not in self.db:
			self.db.update([msg])
