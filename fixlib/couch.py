import fix42
import couchdb
import copy

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
			if fix42.nojson(k):
				msg[k] = str(v)
		return msg
	
	def get(self, dir, seq):
		return self.db.get('%s-%s' % (dir, seq))
	
	def save(self, dir, msg):
		
		msg = self._encode(msg)
		msg['_id'] = '%s-%s' % (dir, msg['MsgSeqNum'])
		
		lkey = {'in': 0, 'out': 1}[dir]
		if self._last[lkey] < msg['MsgSeqNum']:
			self._last[lkey] = msg['MsgSeqNum']
		
		if msg['_id'] not in self.db:
			self.db.update([msg])
