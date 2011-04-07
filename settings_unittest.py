from settings_common import *

DEBUG = TEMPLATE_DEBUG = False

DATABASE_ENGINE = 'sqlite3'
TEST_DATABASE_NAME = 'unittest.db'

DAISY_PIPELINE_PATH = os.path.join(PROJECT_DIR, '..', '..', 'tmp', 'pipeline')

SERVE_STATIC_FILES = True

SOUTH_TESTS_MIGRATE = False
