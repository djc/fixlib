import asyncore
import util

try:
	import simplejson as json
except ImportError:
	import json


class ChannelServer(asyncore.dispatcher):
	
	def __init__(self, sock, dest):
		asyncore.dispatcher.__init__(self, sock)
		self.dest = dest
		dest.hooks.setdefault('close', []).append(self.closehook)
	
	def handle_accept(self):
		client = self.accept()
		SideChannel(client[0], self.dest)
	
	def closehook(self, hook, data):
		self.close()

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
			msg = util.json_decode(json.loads(raw))
			self.dest.queue(msg)
			self.buffer = {'result': 'done'}
	
	def writable(self):
		return self.buffer
	
	def handle_write(self):
		self.send(json.dumps(self.buffer))
		self.close()
