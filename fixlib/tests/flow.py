from datetime import date, datetime

import engine
import unittest, asyncore, socket

class MemoryStore(object):

	def __init__(self):
		self._last = [0, 0]
		self.msgs = {'out': {}, 'in': {}}
	
	@property
	def last(self):
		return self._last
	
	def get(self, dir, seq):
		return self.msgs[dir][seq]
	
	def save(self, dir, msg):
		lkey = {'in': 0, 'out': 1}[dir]
		if self._last[lkey] < msg['MsgSeqNum']:
			self._last[lkey] = msg['MsgSeqNum']
			self.msgs[dir][msg['MsgSeqNum']] = msg
		
def chook(hook, data):
	print 'client', hook, repr(data)
		
def ahook(hook, data):
	print 'server', hook, repr(data)

class EngineTests(unittest.TestCase):
	
	def testlogon(self):
		
		def cond(hook, msg):
			if hook == 'admin' and msg['MsgType'] == 'Logon':
				self.assertEquals(msg['SenderCompID'], 'B')
				self.assertEquals(msg['TargetCompID'], 'A')
				d.close()
				cl.close()
		
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind(('', 32439))
		d = engine.AcceptorServer(sock, MemoryStore())
		d.listen(1)
		d.hooks = {}
		
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect(('127.0.0.1', 32439))
		cl = engine.Initiator(sock, ('A', 'B'), MemoryStore())
		cl.hooks = {'admin': [cond]}
		
		cl.queue({
			'MsgType': 'Logon',
			'HeartBtInt': 60,
			'EncryptMethod': None,
		})
		
		asyncore.loop()

if __name__ == '__main__':
	unittest.main()
