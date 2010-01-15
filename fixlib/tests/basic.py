from datetime import date, datetime

import fix42
import unittest

class ConstructionTests(unittest.TestCase):
	
	def testlogon(self):
		raw = fix42.construct({
			'MsgType': 'Logon',
			'HeartBtInt': 60,
			'EncryptMethod': None,
		})
		v = '8=FIX.4.2\x019=17\x0135=A\x0198=0\x01108=60\x0110=001\x01'
		self.assertEquals(raw, v)
	
	def testtypes(self):
		raw = fix42.construct({
			'MsgType': 'Logon',
			'ExecInst': ['1', '2', '3'],
			'PossDupFlag': True,
			'BeginSeqNo': 3,
			'CumQty': 15.3,
			'TradeDate': date(2010, 1, 15),
			'SendingTime': datetime(2010, 1, 15, 11, 10, 33),
		})
		v = '8=FIX.4.2\x019=64\x0135=A\x0152=20100115-11:10:33\x0114=15.3' \
			'\x017=3\x0143=Y\x0175=20100115\x0118=1 2 3\x0110=161\x01'
		self.assertEquals(raw, v)
	

def suite():
	return [BasicTests]

if __name__ == '__main__':
	unittest.main()
