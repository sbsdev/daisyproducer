from settings_common import *

PACKAGE_VERSION = "0.5"

DEBUG = TEMPLATE_DEBUG = True

DAISY_PIPELINE_PATH = os.path.join(PROJECT_DIR, '..', '..', 'tmp', 'pipeline')
EXTERNAL_PATH = os.path.join(PROJECT_DIR, '..', '..', 'tmp')

SERVE_STATIC_FILES = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d %(funcName)s() %(message)s'
            },
        'simple': {
            'format': '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
            },
        },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
            },
        'abacus': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/daisyproducer_abacus_import.log',
            'formatter': 'simple'
            },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/daisyproducer.log',
            'formatter': 'simple'
            },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
            },
        },
    'loggers': {
        'abacus': {
            'handlers': ['null'],
            'level': 'DEBUG',
            'propagate': False,
            },
        'daisyproducer.documents': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
            },
        },
    }

# the following is an idea from https://code.djangoproject.com/wiki/SplitSettings
# We have both local settings and common settings. They are used as follows:
# - common settings are shared data between normal settings and unit test settings
# - local settings are used on productive servers to keep the local
#   settings such as db passwords, etc out of version control
try:
    from settings_local import *
except ImportError:
    pass
