from settings_unittest import *

TEST_RUNNER='documents.tests_with_coverage.test_runner'
 
# List of modules to enable for code coverage
COVERAGE_MODULES = [
    'documents.views.browse', 
    'documents.views.manage', 
    'documents.views.todo', 
    'documents.models',
    'documents.external',
    'documents.versionHelper'
    ]
