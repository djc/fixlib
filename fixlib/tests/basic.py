from datetime import date, datetime

import fix42
import unittest

class ConstructionTests(unittest.TestCase):
	
	def setUp(self):
		fix42.REPEAT['Legs'].append('MiscFees')
	
	def tearDown(self):
		fix42.REPEAT['Legs'].remove('MiscFees')
	
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
	
	def testgroups(self):
		raw = fix42.construct({
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
		})
		v = '8=FIX.4.2\x019=55\x0135=8\x01136=2\x01137=3.4\x01138=EUR\x01' \
			'139=7\x01137=1.2\x01138=USD\x01139=2\x0110=107\x01'
		self.assertEquals(raw, v)

	def testnestedgroups(self):
		raw = fix42.construct({
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
		})
		# This message is actually incorrect according to spec
		# because the first group in 555 starts with 654, the second group
		# should do the same. Not sure if this comes up in the real world.
		v = '8=FIX.4.2\x019=86\x0135=8\x01555=2\x01654=alpha\x01136=2\x01' \
			'137=3.4\x01138=EUR\x01139=7\x01137=1.2\x01138=USD\x01139=2\x01' \
			'600=B\x01654=beta\x0110=240\x01'
		self.assertEquals(raw, v)

def suite():
	return [BasicTests]

if __name__ == '__main__':
	unittest.main()
