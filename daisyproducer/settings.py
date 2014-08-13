from settings_common import *

PACKAGE_VERSION = "0.5"

DEBUG = TEMPLATE_DEBUG = True

DAISY_PIPELINE_PATH = os.path.join(PROJECT_DIR, '..', '..', 'tmp', 'pipeline')
EXTERNAL_PATH = os.path.join(PROJECT_DIR, '..', '..', 'tmp')

SERVE_STATIC_FILES = True

# the following is an idea from https://code.djangoproject.com/wiki/SplitSettings
# We have both local settings and common settings. They are used as follows:
# - common settings are shared data between normal settings and unit test settings
# - local settings are used on productive servers to keep the local
#   settings such as db passwords, etc out of version control
try:
    from settings_local import *
except ImportError:
    pass
