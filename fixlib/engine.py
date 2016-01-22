# Copyright (C) 2010 KenTyde BV
# All rights reserved.
#
# This software is licensed as described in the file LICENSE,
# which you should have received as part of this distribution.

from __future__ import print_function
from datetime import datetime
from . import fix42

import asyncore, traceback

class Engine(asyncore.dispatcher):
	
	def __init__(self, sock, map=None):
		asyncore.dispatcher.__init__(self, sock, map)
		self.closed = False
		self.hooks = {}
	
	def register(self, type, hook):
		self.hooks.setdefault(type, []).append(hook)
	
	@property
	def next(self):
		return self.store.last[1] + 1
	
	def handle_close(self):
		self.closed = True
		self.hook('close')
		self.close()
	
	def hook(self, hook, data=None):
		for fun in self.hooks.get(hook, []):
			fun(hook, data)
	
	def handle_read(self):
		
		bits = [self.recv(8192)]
		while len(bits[-1]) == 8192:
			bits.append(self.recv(8192))
		
		raw = ''.join(bits)
		self.hook('recv', raw)
		msgs = fix42.parse(raw)
		for msg in msgs:
			self.process(msg)
	
	def writable(self):
		return self.buffer
	
	def handle_write(self):
		sent = self.send(self.buffer[0])
		if len(self.buffer[0]) == sent:
			self.buffer.pop(0)
		else:
			self.buffer[0] = self.buffer[0][sent:]
	
	def queue(self, msg):
		
		if 'MsgSeqNum' not in msg:
			msg['MsgSeqNum'] = self.next
		
		if 'SendingTime' not in msg:
			msg['SendingTime'] = datetime.utcnow()
			msg['SenderCompID'] = self.parties[0]
			msg['TargetCompID'] = self.parties[1]
			self.store.save('out', msg)
		
		self.hook('write', msg)
		try:
			raw = fix42.construct(msg)
		except Exception:
			print('failed to construct %s:' % msg)
			traceback.print_exc()
			return
		
		self.hook('send', raw)
		self.buffer.append(raw)
	
	def resend(self, req):
		start, end = req['BeginSeqNo'], req['EndSeqNo']
		fill, cur = None, start
		for i in range(start, end + 1):
			
			msg = self.store.get('out', i)
			if msg is None or msg['MsgType'] in fix42.IGNORE:
				fill = i
				continue
			
			if fill is not None:
				self.queue({
					'MsgType': 'Sequence Reset',
					'MsgSeqNum': cur,
					'GapFillFlag': True,
					'NewSeqNo': fill + 1,
				})
				fill = None
			
			msg['PossDupFlag'] = True
			self.queue(msg)
			cur += 1
		
		if fill is not None:
			self.queue({
				'MsgType': 'Sequence Reset',
				'MsgSeqNum': cur,
				'GapFillFlag': True,
				'NewSeqNo': fill + 1,
			})

	def process(self, msg):
		type = 'admin' if msg['MsgType'] in fix42.ADMIN else 'app'
		self.hook(type, msg)
		if msg['MsgSeqNum'] > self.store.last[0] + 1:
			rsp = {'MsgType': 'Resend Request', 'EndSeqNo': 0}
			rsp['BeginSeqNo'] = self.store.last[0] + 1
			rsp['EndSeqNo'] = msg['MsgSeqNum'] - 1
			self.queue(rsp)
		self.store.save('in', msg)
		if msg['MsgType'] == 'Test Request':
			rsp = {'MsgType': 'HeartBeat', 'TestReqID': msg['TestReqID']}
			self.queue(rsp)
		elif msg['MsgType'] == 'HeartBeat':
			self.queue({'MsgType': 'HeartBeat'})
		elif msg['MsgType'] == 'Resend Request':
			self.resend(msg)

class Initiator(Engine):
	
	def __init__(self, sock, store, parties, map=None):
		Engine.__init__(self, sock, map)
		self.store = store
		self.buffer = []
		self.parties = parties
	
	def logon(self, hbi, em, reset=False, login=None):
		req = {'MsgType': 'Logon', 'HeartBtInt': hbi, 'EncryptMethod': em}
		if reset:
			req.update({'ResetSeqNumFlag': True, 'MsgSeqNum': 1})
		if login:
			req.update({'Username': login[0], 'Password': login[1]})
		self.queue(req)

class AcceptorServer(asyncore.dispatcher):
	
	def __init__(self, sock, store, map=None):
		asyncore.dispatcher.__init__(self, sock, map)
		self.store = store
		self.hooks = {}
	
	def register(self, type, hook):
		self.hooks.setdefault(type, []).append(hook)
	
	def handle_accept(self):
		client = self.accept()
		a = Acceptor(client[0], self.store, self._map)
		a.hooks = self.hooks

class Acceptor(Engine):
	
	def __init__(self, sock, store, map=None):
		Engine.__init__(self, sock, map)
		self.store = store
		self.buffer = []
		self.parties = None
	
	def process(self, msg):
		if msg['MsgType'] == 'Logon':
			self.parties = msg['TargetCompID'], msg['SenderCompID']
			rsp = {
				'MsgType': 'Logon',
				'HeartBtInt': msg['HeartBtInt'],
				'EncryptMethod': msg['EncryptMethod'],
			}
			if msg.get('ResetSeqNumFlag'):
				rsp.update({'ResetSeqNumFlag': True})
			self.queue(rsp)
		Engine.process(self, msg)
