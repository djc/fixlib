from datetime import date, datetime
from fixlib import fix42

import unittest

class BasicTests(unittest.TestCase):
	
	def setUp(self):
		fix42.REPEAT['Legs'].add('MiscFees')
	
	def tearDown(self):
		fix42.REPEAT['Legs'].remove('MiscFees')
	
	def _parseclean(self, raw):
		msg = fix42.parse(raw)[0]
		msg.pop('BeginString')
		msg.pop('BodyLength')
		msg.pop('CheckSum')
		return msg
	
	def testlogon(self):
		msg = {
			'MsgType': 'Logon',
			'HeartBtInt': 60,
			'EncryptMethod': None,
		}
		raw = fix42.construct(msg)
		v = '8=FIX.4.2\x019=17\x0135=A\x0198=0\x01108=60\x0110=001\x01'
		self.assertEquals(raw, v)
		self.assertEquals(msg, self._parseclean(raw))
	
	def testtypes(self):
		msg = {
			'MsgType': 'Logon',
			'ExecInst': ['Not held', 'Work', 'Go along'],
			'PossDupFlag': True,
			'BeginSeqNo': 3,
			'CumQty': 15.3,
			'TradeDate': date(2010, 1, 15),
			'SendingTime': datetime(2010, 1, 15, 11, 10, 33),
		}
		raw = fix42.construct(msg)
		v = '8=FIX.4.2\x019=64\x0135=A\x0152=20100115-11:10:33\x0114=15.3' \
			'\x017=3\x0143=Y\x0175=20100115\x0118=1 2 3\x0110=161\x01'
		self.assertEquals(raw, v)
		self.assertEquals(msg, self._parseclean(raw))
	
	def testgroups(self):
		msg = {
			'MsgType': 'ExecutionReport',
			'MiscFees': [
				{
					'MiscFeeAmt': 3.4,
					'MiscFeeCurr': 'EUR',
					'MiscFeeType': 'Other',
				}, {
					'MiscFeeAmt': 1.2,
					'MiscFeeCurr': 'USD',
					'MiscFeeType': 'Tax',
				},
			],
		}
		raw = fix42.construct(msg)
		v = '8=FIX.4.2\x019=55\x0135=8\x01136=2\x01137=3.4\x01138=EUR\x01' \
			'139=7\x01137=1.2\x01138=USD\x01139=2\x0110=107\x01'
		self.assertEquals(raw, v)
		self.assertEquals(msg, self._parseclean(raw))

	def testnestedgroups(self):
		msg = {
			'MsgType': 'ExecutionReport',
			'Legs': [
				{
					'LegRefID': 'alpha',
					'MiscFees': [
						{
							'MiscFeeAmt': 3.4,
							'MiscFeeCurr': 'EUR',
							'MiscFeeType': 'Other',
						}, {
							'MiscFeeAmt': 1.2,
							'MiscFeeCurr': 'USD',
							'MiscFeeType': 'Tax',
						},
					],
				},
				{
					'LegRefID': 'beta',
					'LegSymbol': 'B',
				},
			]
		}
		raw = fix42.construct(msg)
		v = '8=FIX.4.2\x019=86\x0135=8\x01555=2\x01654=alpha\x01136=2\x01' \
			'137=3.4\x01138=EUR\x01139=7\x01137=1.2\x01138=USD\x01139=2\x01' \
			'654=beta\x01600=B\x0110=240\x01'
		self.assertEquals(raw, v)
		self.assertEquals(msg, self._parseclean(raw))

def suite():
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(BasicTests, 'test'))
	return suite

if __name__ == '__main__':
	unittest.main(defaultTest='suite')
