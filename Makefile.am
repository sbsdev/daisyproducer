SUBDIRS = doc documents templates

python_PYTHON = __init__.py manage.py settings.py settings_common.py settings_unittest.py settings_unittest_with_coverage.py urls.py utils.py

EXTRA_DIST = public daisyproducer.wsgi test.sh

TESTS = test.sh

check-coverage:
	django-admin test --pythonpath=. --settings=settings_unittest_with_coverage
