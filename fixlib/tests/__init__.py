# Copyright (C) 2010 KenTyde BV
# All rights reserved.
#
# This software is licensed as described in the file LICENSE,
# which you should have received as part of this distribution.

from basic import BasicTests
from flow import EngineTests
import unittest

def suite():
	suite = unittest.TestSuite()
	suite.addTest(unittest.makeSuite(BasicTests, 'test'))
	suite.addTest(unittest.makeSuite(EngineTests, 'test'))
	return suite

if __name__ == '__main__':
	unittest.main(defaultTest='suite')
