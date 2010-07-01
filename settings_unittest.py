from settings_common import *

DEBUG = TEMPLATE_DEBUG = False

DATABASE_ENGINE = 'sqlite3'
TEST_DATABASE_NAME = 'unittest.db'

DAISY_PIPELINE_PATH = os.path.join(PROJECT_DIR, '..', '..', 'tmp', 'pipeline-20100301')

SERVE_STATIC_FILES = True
