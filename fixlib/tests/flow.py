# Copyright (C) 2010 KenTyde BV
# All rights reserved.
#
# This software is licensed as described in the file LICENSE,
# which you should have described as part of this distribution.

from fixlib import engine, channel

import unittest, asyncore, socket, json

TEST_PORT = 32349
CHANNEL_PORT = 20111

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
	
	def setup(self, chan=False):
		
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind(('', TEST_PORT))
		a = engine.AcceptorServer(sock, MemoryStore())
		a.listen(1)
		
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect(('127.0.0.1', TEST_PORT))
		i = engine.Initiator(sock, MemoryStore(), ('A', 'B'))
		
		if not chan:
			return i, a
		
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind(('', CHANNEL_PORT))
		c = channel.ChannelServer(sock, i)
		c.listen(1)
		
		return i, a, c
	
	def loop(self, i, a, icond=None, acond=None, reset=False):
		
		if icond is not None:
			i.register('app', icond)
			i.register('admin', icond)
		if acond is not None:
			a.register('app', acond)
			a.register('admin', acond)
		
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
	
	def testchannel(self):
		
		i, a, c = self.setup(True)
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		def icond(hook, msg):
			if hook == 'admin' and msg['MsgType'] == 'Logon':
				sock.connect(('127.0.0.1', CHANNEL_PORT))
				sock.send(json.dumps({'MsgType': 'NewOrderSingle'}))
		
		def acond(hook, msg):
			if hook == 'app' and msg['MsgType'] == 'NewOrderSingle':
				a.close()
				i.close()
				c.close()
		
		self.loop(i, a, icond, acond, False)
		self.assertEqual(json.loads(sock.recv(8192)), {'result': 'done'})

def suite():
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(EngineTests, 'test'))
	return suite
	
if __name__ == '__main__':
	unittest.main(defaultTest='suite')
