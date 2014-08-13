SUBDIRS = doc web

PO_FILES = locale/de/LC_MESSAGES/django.po
MO_FILES = $(PO_FILES:.po=.mo)

PYTHON_FILES = \
	$(wildcard *.py) \
	$(wildcard documents/*.py) \
	$(wildcard documents/templatetags/*.py) \
	$(wildcard documents/views/*.py)

TEMPLATE_FILES = \
	$(wildcard templates/*.html) \
	$(wildcard templates/documents/*.html) \
	templates/DTBookTemplate.xml

TEST_FILES = \
	$(wildcard documents/test/*.py) \
	$(wildcard documents/test/functional/*.py) \
	$(wildcard documents/test/unit/*.py) \
	$(wildcard documents/fixtures/*.yaml)

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
