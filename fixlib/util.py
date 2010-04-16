# Copyright (C) 2010 KenTyde BV
# All rights reserved.
#
# This software is licensed as described in the file LICENSE,
# which you should have received as part of this distribution.

from datetime import datetime, date

import fix42
import copy

def ddecode(s):
	return datetime.strptime(s, '%Y-%m-%d').date()

def dtdecode(s):
	return datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

TYPES = {
	date: (str, ddecode),
	datetime: (lambda s: str(s)[:19], dtdecode),
}

def json_encode(msg):
	msg = copy.copy(msg)
	for k, v in msg.iteritems():
		
		if k in fix42.REPEAT:
			msg[k] = [json_encode(i) for i in v]
		else:
			codec = TYPES.get(fix42.WTAGS[k][1])
			msg[k] = v if codec is None else codec[0](v)
		
	return msg

def json_decode(msg):
	new = {}
	for k, v in msg.iteritems():
		
		if k.startswith('_'):
			continue
		
		if k in fix42.REPEAT:
			v = [json_decode(i) for i in v]
		else:
			codec = TYPES.get(fix42.WTAGS[k][1])
			v = v if codec is None else codec[1](v)
		
		new[k] = v
	
	return new
