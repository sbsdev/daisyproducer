SUBDIRS = doc

PYTHON_FILES = \
	$(wildcard *.py) \
	$(wildcard documents/*.py) \
	$(wildcard documents/templatetags/*.py) \
	$(wildcard documents/views/*.py) \
	documents/sql/state.sql \
	documents/xslt/brailleSanitize.xsl

TEMPLATE_FILES = \
	$(wildcard templates/*.html) \
	$(wildcard templates/documents/*.html) \
	templates/DTBookTemplate.xml

PUBLIC_FILES = \
	public/images/edit.png \
	public/javascripts/prototype.js \
	public/stylesheets/application.css

TEST_FILES = \
	$(wildcard documents/test/*.py) \
	$(wildcard documents/test/functional/*.py) \
	$(wildcard documents/test/unit/*.py) \
	$(wildcard documents/fixtures/*.yaml) \
	$(wildcard documents/test/data/*) \
	test.sh

DOC_FILES = $(wildcard doc/help/*.txt)

nobase_dist_pkgdata_DATA = \
	$(PYTHON_FILES) \
	$(TEMPLATE_FILES) \
	$(PUBLIC_FILES) \
	$(TEST_FILES) \
	$(DOC_FILES) \
	daisyproducer.wsgi

TESTS = test.sh

check-coverage:
	django-admin test --pythonpath=. --settings=settings_unittest_with_coverage
