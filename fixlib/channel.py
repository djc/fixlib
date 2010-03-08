from datetime import datetime, date
from collections import deque

import asyncore
import copy
import fix42

try:
	import simplejson as json
except ImportError:
	import json

def ddecode(s):
	return datetime.strptime(s, '%Y-%m-%d %H:%M:%S').date()

def dtdecode(s):
	return datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

TYPES = {
	date: (str, ddecode),
	datetime: (lambda s: str(s)[:19], dtdecode),
}

class ChannelServer(asyncore.dispatcher):
	
	def __init__(self, sock, dest):
		asyncore.dispatcher.__init__(self, sock)
		self.dest = dest
	
	def handle_accept(self):
		client = self.accept()
		SideChannel(client[0], self.dest)


class SideChannel(asyncore.dispatcher):
	
	def __init__(self, sock, dest):
		asyncore.dispatcher.__init__(self, sock)
		self.dest = dest
		self.buffer = None
	
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
	
	def handle_close(self):
		self.close()
	
	def handle_read(self):
		raw = self.recv(8192)
		if raw:
			msg = self._decode(json.loads(raw))
			self.dest.queue(msg)
			self.buffer = {'result': 'done'}
	
	def writable(self):
		return self.buffer
	
	def handle_write(self):
		self.send(json.dumps(self.buffer))
		self.close()
