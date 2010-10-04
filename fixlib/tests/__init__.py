# Copyright (C) 2010 KenTyde BV
# All rights reserved.
#
# This software is licensed as described in the file LICENSE,
# which you should have received as part of this distribution.

import basic, flow
import unittest

def suite():
	suite = unittest.TestSuite()
	suite.addTest(basic.suite())
	suite.addTest(flow.suite())
	return suite

if __name__ == '__main__':
	unittest.main(defaultTest='suite')
