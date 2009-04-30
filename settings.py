from settings_common import *

DEBUG = TEMPLATE_DEBUG = True

DATABASE_ENGINE = 'postgresql_psycopg2'
DATABASE_NAME = 'daisyproducer_dev'
DATABASE_USER = 'eglic'
DATABASE_PASSWORD = ''

DAISY_PIPELINE_PATH = os.path.join(PROJECT_DIR, '..', '..', 'tmp', 'pipeline-20090410')
