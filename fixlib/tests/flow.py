from datetime import date, datetime

import engine
import unittest, asyncore, socket

TEST_PORT = 32349

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

class EngineTests(unittest.TestCase):
	
	def setup(self):
		
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind(('', TEST_PORT))
		a = engine.AcceptorServer(sock, MemoryStore())
		a.listen(1)
		
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect(('127.0.0.1', TEST_PORT))
		i = engine.Initiator(sock, ('A', 'B'), MemoryStore())
		
		return i, a
	
	def loop(self, i, a, icond=None, acond=None):
		
		if icond is not None:
			i.hooks = {'app': [icond], 'admin': [icond]}
		if acond is not None:
			a.hooks = {'app': [acond], 'admin': [acond]}
		
		i.queue({
			'MsgType': 'Logon',
			'HeartBtInt': 5,
			'EncryptMethod': None,
		})
		asyncore.loop()
	
	def testlogon(self):
		i, a = self.setup()
		def cond(hook, msg):
			if hook == 'admin' and msg['MsgType'] == 'Logon':
				self.assertEquals(msg['SenderCompID'], 'B')
				self.assertEquals(msg['TargetCompID'], 'A')
				a.close()
				i.close()
		self.loop(i, a, cond, None)

if __name__ == '__main__':
	unittest.main()
