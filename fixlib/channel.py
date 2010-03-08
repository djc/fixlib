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
		self.buffer = deque
	
	def handle_accept(self):
		client = self.accept()
		SideChannel(client[0], self.dest)


class SideChannel(asyncore.dispatcher):
	
	def __init__(self, sock, dest):
		asyncore.dispatcher.__init__(self, sock)
		self.dest = dest
	
	def handle_close(self):
		self.close()
	
	def handle_read(self):
		raw = self.recv(8192)
		if raw:
			msg = json.loads(raw)
			self.dest.queue(msg)
	
	def writable(self):
		return False
