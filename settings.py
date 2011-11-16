from settings_common import *

PACKAGE_VERSION = "0.5"

DEBUG = TEMPLATE_DEBUG = True

DATABASE_ENGINE = 'postgresql_psycopg2'
DATABASE_NAME = 'daisyproducer_dev'
DATABASE_USER = 'eglic'
DATABASE_PASSWORD = ''

DAISY_PIPELINE_PATH = os.path.join(PROJECT_DIR, '..', '..', 'tmp', 'pipeline')
DTBOOK2SBSFORM_PATH = os.path.join(PROJECT_DIR, '..', 'LiblouisSaxonExtension')

# debug toolbar
#INSTALLED_APPS +=  ('debug_toolbar',)
#MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_CONFIG = {'INTERCEPT_REDIRECTS' : False}
SERVE_STATIC_FILES = True
