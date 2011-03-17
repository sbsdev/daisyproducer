SUBDIRS = doc web

PO_FILES = locale/de/LC_MESSAGES/django.po
MO_FILES = $(PO_FILES:.po=.mo)

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
	$(wildcard documents/fixtures/*.yaml)

TEST_DATA_FILES = \
	$(wildcard documents/test/data/*)

DOC_FILES = \
	$(wildcard doc/help/*.txt) \
	README.rst \
	INSTALL.rst

nobase_dist_pkgdata_DATA = \
	$(PO_FILES) \
	$(MO_FILES) \
	$(PYTHON_FILES) \
	$(TEMPLATE_FILES) \
	$(PUBLIC_FILES) \
	$(XOPUS_FILES) \
	$(TEST_FILES) \
	$(TEST_DATA_FILES) \
	$(DOC_FILES) \
	daisyproducer.wsgi

# TAGS
ETAGS_ARGS = $(PYTHON_FILES) $(TEST_FILES) $(TEMPLATE_FILES)

# i18n
%.mo: %.po
	django-admin compilemessages

clean-local:
	rm -f $(MO_FILES)

# Testing
check:
	django-admin test --pythonpath=. --settings=settings_unittest

check-coverage:
	django-admin test --pythonpath=. --settings=settings_unittest_with_coverage

# Deployment
deploy_test:
	ssh xmlp-test ~/updateDaisyProducer.sh test

deploy_production:
	ssh xmlp ~/updateDaisyProducer.sh production
