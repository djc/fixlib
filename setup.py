#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 KenTyde
# All rights reserved.
#
# This software is licensed as described in the file LICENSE,
# which you should have received as part of this distribution.

from setuptools import setup
import os

with open('README.rst') as f:
	desc = f.read()

setup(
	name='fixlib',
	version='0.5',
	description='Pythonic library for dealing with the FIX protocol',
	long_description=desc,
	author='Dirkjan Ochtman',
	author_email='dirkjan@ochtman.nl',
	license='BSD',
	url='https://github.com/djc/fixlib',
	classifiers=[
		'Development Status :: 4 - Beta',
		'Intended Audience :: Financial and Insurance Industry',
		'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
	],
	packages=['fixlib'],
	test_suite='fixlib.tests.suite',
)
