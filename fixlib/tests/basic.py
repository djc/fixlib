# Copyright (C) 2010 KenTyde BV
# All rights reserved.
#
# This software is licensed as described in the file LICENSE,
# which you should have described as part of this distribution.

from datetime import date, datetime
from fixlib import fix42, util

import unittest

class BasicTests(unittest.TestCase):
	
	def setUp(self):
		fix42.REPEAT['Legs'].append('MiscFees')
		fix42.REPEAT['Legs'].append('TransactTime')
	
	def tearDown(self):
		fix42.REPEAT['Legs'].remove('MiscFees')
		fix42.REPEAT['Legs'].remove('TransactTime')
	
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
		self.assertEqual(raw, v)
		self.assertEqual(msg, self._parseclean(raw))
	
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
		v = '8=FIX.4.2\x019=64\x0135=A\x0152=20100115-11:10:33\x017=3\x01' \
			'14=15.3\x0118=1 2 3\x0143=Y\x0175=20100115\x0110=161\x01'
		self.assertEqual(raw, v)
		self.assertEqual(msg, self._parseclean(raw))
	
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
		self.assertEqual(raw, v)
		self.assertEqual(msg, self._parseclean(raw))

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
		self.assertEqual(raw, v)
		self.assertEqual(msg, self._parseclean(raw))
	
	def testjson(self):
		dt = datetime(2010, 3, 9, 12, 45, 43)
		msg = {
			'MsgType': 'ExecutionReport',
			'Legs': [
				{
					'TransactTime': dt,
				}
			],
			'SendingTime': dt,
			'TradeDate': date(2010, 4, 15),
		}
		x = util.json_encode(msg)
		self.assertEqual(x['SendingTime'], '2010-03-09 12:45:43')
		self.assertEqual(x['Legs'][0]['TransactTime'], '2010-03-09 12:45:43')
		self.assertEqual(x['TradeDate'], '2010-04-15')
		self.assertEqual(util.json_decode(x), msg)
	
	def testdatetimes(self):
		dt = fix42.dtdecode('20100323-14:23:21.123')
		test = datetime(2010, 3, 23, 14, 23, 21, 123000)
		self.assertEqual(dt, test)
		dt = fix42.dtdecode('20100323-14:24:21')
		test = datetime(2010, 3, 23, 14, 24, 21)
		self.assertEqual(dt, test)
	
def suite():
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(BasicTests, 'test'))
	return suite

if __name__ == '__main__':
	unittest.main(defaultTest='suite')
