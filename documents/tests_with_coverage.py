"""
tests_with_coverage.py - clone of django.test.simple.run_tests with coverage functionality.
Based on http://siddhi.blogspot.com/2007/04/code-coverage-for-your-django-code.html

To use this module put
TEST_RUNNER = 'documents.tests_with_coverage.test_runner'
into settings.py.

You can use COVERAGE_MODULES in settings.py to configure for which
modules you want want to be analyzed for coverage. If COVERAGE_MODULES
is left empty the whole coverage engine is turned of and thus there is
nearly no overhead.

COVERAGE_MODULES = ['documents.views.browse', 'documents.models']
"""

import unittest, os, coverage

from django.conf import settings
from django.test.simple import run_tests as django_test_runner

def test_runner(test_labels, verbosity=1, interactive=True, extra_tests=[]):
    coveragemodules = []
    if hasattr(settings, 'COVERAGE_MODULES'):
        coveragemodules = settings.COVERAGE_MODULES
    if coveragemodules and not test_labels:
        coverage.use_cache(0)
        coverage.start()

    test_results = django_test_runner(test_labels, verbosity, interactive, extra_tests)

    if coveragemodules and not test_labels:
        coverage.stop()
        print ''
        print '----------------------------------------------------------------------'
        print ' Unit Test Code Coverage Results'
        print '----------------------------------------------------------------------'
        modules = []
        for module_string in coveragemodules:
            modules.append(__import__(module_string, globals(), locals(), [""]))
        coverage.report(modules, show_missing=1)
        print '----------------------------------------------------------------------'

    return test_results

