=====================
Daisy Producer README
=====================

What is it?
===========

`Daisy Producer`_ is a system to help you manage the production
process of accessible media. It assumes that you are transforming the
content from hard copy or any electronic format to `DTBook XML`_. Once
you have the DTBook XML the `Daisy Pipeline`_ and liblouis_ can be
used to generate Daisy Talking Books, Large Print and Braille in a
fully automated way.

Daisy producer mainly tracks the status of the transformation process
and helps you manage your artifacts that are needed in the
transformation process.

For the generation of accessible media Daisy Producer offers a nice
interface however the work is essentially done by the Daisy Pipeline
and liblouis.

.. _Daisy Producer: http://www.daisy-producer.org
.. _DTBook XML: http://www.daisy.org/projects/pipeline/
.. _Daisy Pipeline: http://www.daisy.org/projects/pipeline/
.. _liblouis: http://code.google.com/p/liblouis/

About
=====
`Daisy Producer`_ is released under the terms of the `GNU Affero
General Public License (AGPL)`_.

.. _GNU Affero General Public License (AGPL): http://www.gnu.org/licenses/agpl.html

How to participate
==================
To participate in discussion and development, subscribe to our `mailing
list`_, fetch the code from the `code repository`_ or submit bugs in the
`issue tracker`_.

.. _mailing list:
.. _code repository: http://github.com/egli/daisy-producer
.. _issue tracker: http://github.com/egli/daisy-producer/issues

Download
========
The latest release of `Daisy Producer`_ is available from the
`download page`_.

.. _download page: http://github.com/egli/daisy-producer/downloads

Documentation
=============
`Daisy Producer`_ comes with built in documentation. See the `Help
link`_ in your installation.

.. _Help link: http://127.0.0.1:8000/help/


.. Frequently Asked Questions
.. ==========================

.. Why is daisyproducer not using distutils or setuptools
.. ------------------------------------------------------
.. The basic requirements for a build and distribution utility are
.. support for building a source distribution, support for installation
.. and deinstallation and finally support for test invocation. 

.. While distutils_ seems to be the standard in the Python world it has
.. no built-in support for running a test suite. setuptools_ seem to be a
.. modern version of distutils and do support invocation of a test suite
.. albeit in a limited way. Thirdly and apparently currently most trendy
.. is there is buildout_ which seems to support all of this and way more.
.. All of these tools seem to either add an unnecessary level of
.. complexity for little gain.

.. Lastly there are the tried and true autotools_ which lets you add
.. anything to the Makefile. While they do not support many of the
.. advanced features like dependency tracking and are crud in many ways
.. they still provide a fairly simple way to package, test and install
.. software.

.. .. _distutils: http://docs.python.org/distutils/
.. .. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
.. .. _buildout: http://jacobian.org/writing/django-apps-with-buildout/
.. .. _autotools: http://en.wikipedia.org/wiki/GNU_build_system
