from collections import deque
import asyncore

try:
	import simplejson as json
except ImportError:
	import json


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
	
	def handle_close(self):
		self.close()
	
	def handle_read(self):
		raw = self.recv(8192)
		if raw:
			msg = json.loads(raw)
			self.dest.queue(msg)
			self.buffer = {'result': 'done'}
	
	def writable(self):
		return self.buffer
	
	def handle_write(self):
		self.send(json.dumps(self.buffer))
		self.close()
