from settings_common import *

DEBUG = TEMPLATE_DEBUG = False

DATABASE_ENGINE = 'sqlite3'
# FIXME: This should be changed to the new TEST setting
# (https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-DATABASE-TEST).
# Will be deprecated in Django 1.9
TEST_DATABASE_NAME = 'unittest.db'

DAISY_PIPELINE_PATH = os.path.join(PROJECT_DIR, '..', '..', 'tmp', 'pipeline')
EXTERNAL_PATH = os.path.join(PROJECT_DIR, '..')

SERVE_STATIC_FILES = True
