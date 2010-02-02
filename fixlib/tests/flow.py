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
		i = engine.Initiator(sock, MemoryStore(), ('A', 'B'))
		
		return i, a
	
	def loop(self, i, a, icond=None, acond=None, reset=False):
		
		if icond is not None:
			i.hooks = {'app': [icond], 'admin': [icond]}
		if acond is not None:
			a.hooks = {'app': [acond], 'admin': [acond]}
		
		i.logon(5, None, reset)
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
	
	def testreset(self):
		i, a = self.setup()
		def cond(hook, msg):
			if hook == 'admin' and msg['MsgType'] == 'Logon':
				self.assertEquals(msg.get('ResetSeqNumFlag'), True)
				self.assertEquals(msg['MsgSeqNum'], 1)
				a.close()
				i.close()
		self.loop(i, a, cond, None, True)
	
	
if __name__ == '__main__':
	unittest.main()
