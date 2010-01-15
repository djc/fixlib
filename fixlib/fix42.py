from datetime import datetime, date

import copy

SOH = '\x01'
DATEFMT = '%Y%m%d'
DATETIMEFMT = '%Y%m%d-%H:%M:%S'
PROTO = 'FIX.4.2'
CSMASK = 255

ADMIN = set([
	'Logon', 'Logout', 'Resend Request', 'HeartBeat', 'Test Request',
	'SeqReset-Reset', 'SeqReset-GapFill', 'Reject',
])

IGNORE = ADMIN - set(['Reject'])

WENUMS = {
	'EncryptMethod': {
		None: 0,
	},
	'MsgType': {
		'HeartBeat': '0',
		'Test Request': '1',
		'Resend Request': '2',
		'Sequence Reset': '4',
		'Logout': '5',
		'ExecutionReport': '8',
		'OrderCancelReject': '9',
		'Logon': 'A',
		'NewOrderSingle': 'D',
		'OrderCancelRequest': 'F',
		'OrderCancelReplaceRequest': 'G',
		'OrderStatusRequest': 'H',
		'DKTrade': 'Q',
		'Multi-Leg': 'AB',
		'Multi-Leg Replace': 'AC',
	},
	'Side': {
		'Buy': '1',
		'Sell': '2',
	},
	'OrdType': {
		'Market': '1',
		'Limit': '2',
		'Stop': '3',
		'Stop limit': '4',
		'Market on close': '5',
		'With or without': '6',
		'Limit or better': '7',
		'Limit with or without': '8',
	},
	'OpenClose': {
		'Open': 'O',
		'Close': 'C',
	},
	'PutOrCall': {
		'Put': 0,
		'Call': 1,
	},
	'ExecTransType': {
		'New': '0',
		'Cancel': '1',
		'Correct': '2',
		'Status': '3',
	},
	'OrdStatus': {
		'New': '0',
		'Partially filled': '1',
		'Filled': '2',
		'Done for day': '3',
		'Canceled': '4',
		'Replaced': '5',
		'Pending Cancel': '6',
		'Stopped': '7',
		'Rejected': '8',
		'Suspended': '9',
		'Pending New': 'A',
		'Calculated': 'B',
		'Expired': 'C',
		'Accepted for bidding': 'D',
		'Pending Replace': 'E',
	},
	'ExecType': {
		'New': '0',
		'Partial fill': '1',
		'Fill': '2',
		'Done for day': '3',
		'Canceled': '4',
		'Replace': '5',
		'Pending Cancel': '6',
		'Stopped': '7',
		'Rejected': '8',
		'Suspended': '9',
		'Pending New': 'A',
		'Calculated': 'B',
		'Expired': 'C',
		'Restated': 'D',
		'Pending Replace': 'E',
	},
	'CxlRejReason': {
		'Too late to cancel': 0,
		'Unknown order': 1,
		'Broker Option': 2,
		'Order already pending': 3,
	},
	'CxlRejResponseTo': {
		'Order Cancel Request': '1',
		'Order Cancel/Replace Request': '2',
	},
	'HandlInst': {
		'auto-private': '1',
		'manual': '3',
	},
	'MultiLegReportingType': {
		'Single Security': '1',
		'Individual leg': '2',
		'Multi-leg': '3',
	},
	'ExecInst': {
		'Not held': '1',
		'Work': '2',
		'Go along': '3',
		'Over the day': '4',
		'Held': '5',
		"Participate don't initiate": '6',
	},
	'MiscFeeType': {
		'Regulatory': '1',
		'Tax': '2',
		'Local Commission': '3',
		'Exchange Fees': '4',
		'Stamp': '5',
		'Levy': '6',
		'Other': '7',
		'Markup': '8',
		'Consumption Tax': '9',
	},
	'ExecRestatementReason': {
		'GT Corporate action': 0,
		'GT renewal / restatement': 1,
		'Verbal change': 2,
		'Repricing of order': 3,
		'Broker option': 4,
		'Partial decline of OrderQty': 5,
	}
}

RENUMS = {}
for tag, vals in WENUMS.iteritems():
	cur = RENUMS.setdefault(tag, {})
	for k, v in vals.iteritems():
		cur[v] = k

def booldecode(x):
	return {'Y': True, 'N': False}[x]

def ddecode(d):
	return datetime.strptime(d, DATEFMT).date()

def dtdecode(dt):
	return datetime.strptime(dt, DATETIMEFMT)

def multi(s):
	return s.split(' ')

WTAGS = {
	'Account': (1, str),
	'AvgPx': (6, float),
	'BeginSeqNo': (7, int),
	'BeginString': (8, str),
	'BodyLength': (9, int),
	'CheckSum': (10, str),
	'ClOrdID': (11, str),
	'CumQty': (14, float),
	'Currency': (15, str),
	'EndSeqNo': (16, int),
	'ExecID': (17, str),
	'ExecInst': (18, multi),
	'ExecRefID': (19, str),
	'ExecTransType': (20, str),
	'HandlInst': (21, str),
	'LastMkt': (30, str),
	'LastPx': (31, float),
	'LastShares': (32, float),
	'MsgSeqNum': (34, int),
	'MsgType': (35, str),
	'NewSeqNo': (36, int),
	'OrderID': (37, str),
	'OrderQty': (38, float),
	'OrdStatus': (39, str),
	'OrdType': (40, str),
	'OrigClOrdID': (41, str),
	'PossDupFlag': (43, booldecode),
	'Price': (44, float),
	'SenderCompID': (49, str),
	'SenderSubID': (50, str),
	'SendingTime': (52, dtdecode),
	'Side': (54, str),
	'Symbol': (55, str),
	'TargetCompID': (56, str),
	'Text': (58, str),
	'TimeInForce': (59, str),
	'TransactTime': (60, dtdecode),
	'TradeDate': (75, ddecode),
	'ExecBroker': (76, str),
	'OpenClose': (77, str),
	'EncryptMethod': (98, int),
	'StopPx': (99, float),
	'ExDestination': (100, str),
	'CxlRejReason': (102, int),
	'HeartBtInt': (108, int),
	'ClientID': (109, str),
	'MaxFloor': (111, float),
	'TestReqID': (112, str),
	'OrigSendingTime': (122, dtdecode),
	'GapFillFlag': (123, booldecode),
	'ExpireTime': (126, dtdecode),
	'NoMiscFees': (136, int),
	'MiscFeeAmt': (137, float),
	'MiscFeeCurr': (138, str),
	'MiscFeeType': (139, str),
	'ExecType': (150, str),
	'LeavesQty': (151, float),
	'SecurityType': (167, str),
	'SecondaryOrderID': (198, str),
	'MaturityMonthYear': (200, str),
	'PutOrCall': (201, int),
	'StrikePrice': (202, float),
	'MaturityDay': (205, str),
	'OptAttribute': (206, str),
	'SecurityExchange': (207, str),
	'ExecRestatementReason': (378, int),
	'DayOrderQty': (424, float),
	'DayCumQty': (425, float),
	'DayAvgPx': (426, float),
	'CxlRejResponseTo': (434, str),
	'ClearingFirm': (439, str),
	'MultiLegReportingType': (442, str),
	'NoLegs': (555, int),
	'LegSymbol': (600, str),
	'LegCFICode': (608, str),
	'LegMaturityMonthYear': (610, str),
	'LegRatioQty': (623, int),
	'LegSide': (624, str),
	'LegRefID': (654, str),
	'TargetStrategy': (847, str),
}

RTAGS = dict((v[0], (k, v[1])) for (k, v) in WTAGS.iteritems())

HEADER = [
	'SenderCompID', 'TargetCompID', 'MsgSeqNum', 'SendingTime',
]

REPEAT = {
	'Legs': [
		'LegSymbol', 'LegCFICode', 'LegMaturityMonthYear', 'LegRatioQty',
		'LegSide', 'LegRefID',
	],
	'MiscFees': [
		'MiscFeeAmt', 'MiscFeeCurr', 'MiscFeeType',
	],
}

SHOW = {
	bool: (lambda x: {True: 'Y', False: 'N'}[x]),
	str: (lambda x: x),
	int: (lambda x: str(x)),
	float: (lambda x: str(x)),
	long: (lambda x: str(x)),
	datetime: (lambda x: x.strftime(DATEFMT)),
}

def nojson(k):
	return WTAGS[k][1] in (dtdecode, ddecode)

def format(k, v):
	if k in WENUMS:
		v = WENUMS[k][v]
	v = SHOW[type(v)](v)
	return '%i=%s' % (WTAGS[k][0], v)

def tags(body, k, v):
	
	if k not in REPEAT:
		body.append(format(k, v))
		return

	body.append(format('No' + k, len(v)))
	for grp in v:
		for key in REPEAT[k]:
			if key in grp:
				tags(body, key, grp[key])

def construct(msg):
	
	msg = copy.copy(msg)
	body = []
	body.append(format('MsgType', msg.pop('MsgType')))
	for k in HEADER:
		if k in msg:
			body.append(format(k, msg.pop(k)))
	
	for k, v in msg.iteritems():
		tags(body, k, v)
	
	body = SOH.join(body) + SOH
	header = [format('BeginString', PROTO)]
	header.append(format('BodyLength', len(body)))
	header.append(body)
	
	data = SOH.join(header)
	cs = sum(ord(c) for c in data) & CSMASK
	return data + format('CheckSum', '%03i' % cs) + SOH

def parse(msg):
	
	tags = msg.split(SOH)
	assert tags[-1] == ''
	tags = tags[:-1]
	
	msgs = [{}]
	parent = [(None, msgs)]
	cur, grp = msgs[0], None
	for tag in tags:
		
		k, v = tag.split('=', 1)
		if int(k) not in RTAGS:
			raise ValueError(int(k))
		
		k, decode = RTAGS[int(k)]
		v = decode(v)
		if k.startswith('No') and k[2:] in REPEAT and v:
			grp = k[2:]
			parent.append((grp, [{}]))
			cur[k[2:]] = parent[-1][1]
			cur = parent[-1][1][0]
			continue
		
		if k not in RENUMS:
			pass
		elif isinstance(v, tuple) or isinstance(v, list):
			v = v.__class__(RENUMS[k].get(i, i) for i in v)
		elif v in RENUMS[k]:
			v = RENUMS[k][v]
		
		if grp and k in cur: # next group
			cur = {}
			parent[-1][1].append(cur)
		elif grp and k not in REPEAT[grp]: # end of current group range
			parent.pop()
			grp = parent[-1][0]
			cur = parent[-1][1][-1]
		
		cur[k] = v
		if k == 'CheckSum':
			cur = {}
			msgs.append(cur)
	
	if not msgs[-1]:
		msgs.pop(-1)	
	return msgs
