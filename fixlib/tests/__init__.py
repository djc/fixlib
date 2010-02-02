import basic, flow
import unittest

def suite():
	suite = unittest.TestSuite()
	suite.addTest(basic.suite())
	suite.addTest(flow.suite())
	return suite

if __name__ == '__main__':
	unittest.main(defaultTest='suite')
