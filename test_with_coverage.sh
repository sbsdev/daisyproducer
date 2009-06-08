#!/bin/sh

django-admin test --pythonpath=. --settings=settings_unittest_with_coverage
