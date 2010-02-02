from datetime import datetime

import fix42
import socket, asyncore

class Engine(asyncore.dispatcher):
	
	@property
	def next(self):
		return self.store.last[1] + 1
	
	def handle_close(self):
		self.close()
	
	def hook(self, hook, data):
		for fun in self.hooks.get(hook, []):
			fun(hook, data)
	
	def handle_read(self):
		raw = self.recv(8192)
		self.hook('recv', raw)
		msgs = fix42.parse(raw)
		for msg in msgs:
			type = 'admin' if msg['MsgType'] in fix42.ADMIN else 'app'
			self.hook(type, msg)
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
		raw = fix42.construct(msg)
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
			
			msg.pop('_id')
			msg.pop('_rev')
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
	
	def __init__(self, sock, parties, store):
		asyncore.dispatcher.__init__(self, sock)
		self.parties = parties
		self.store = store
		self.buffer = []

class AcceptorServer(asyncore.dispatcher):
	
	def __init__(self, sock, store):
		asyncore.dispatcher.__init__(self, sock)
		self.store = store
		self.hooks = {}
	
	def handle_accept(self):
		client = self.accept()
		a = Acceptor(client[0], self.store)
		a.hooks = self.hooks

class Acceptor(Engine):
	
	def __init__(self, sock, store):
		asyncore.dispatcher.__init__(self, sock)
		self.store = store
		self.buffer = []
		self.hooks = {}
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
