
fixlib
======

.. image:: https://travis-ci.org/djc/fixlib.svg?branch=master
   :target: https://travis-ci.org/djc/fixlib
.. image:: https://coveralls.io/repos/djc/fixlib/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/djc/fixlib?branch=master

fixlib provides a Pythonic interface to build FIX engines. FIX messages
(currently, only version 4.2 of the protocol is supported) are converted
to very readable Python dictionaries. An abstract store interface is used
to store messages and thereby provide the resend facilities required by the
protocol. An example store based on CouchDB and couchdb-python is provided.
fixlib uses the asyncore module from the standard library to efficiently
handle network communication.


Requirements
============

* setuptools (for easy running of tests)
* python (tested on 2.7)
* couchdb-python (if using the CouchDB store)


Changelog
=========


Version 1.0 (???)
--------------------------

* Add a side channel to support other processes submitting messages.
* More comprehensive support for the FIX 4.2 standard.
* Better support for repeating groups (in particular wrt ordering).


Version 0.5 (Feb 11, 2010)
--------------------------

* Initial release.


Further information
===================

fixlib is `hosted`_ on GitHub. Any feedback is welcome there.
``views.dump`` contains the design documents needed for the CouchDB store.

.. _hosted: https://github.com/djc/fixlib
