# coding=utf-8
# Django settings for daisyproducer project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

import os.path
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

ADMINS = (
    ('Christian Egli', 'christian.egli@sbs.ch'),
    ('Bert Frees', 'bert.frees@sbs.ch'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'daisyproducer_dev',     # Or path to database file if using sqlite3.
        'USER': 'eglic',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

EMAIL_HOST = 'smtp.sbszh.ch'
MAIL_SUBJECT_PREFIX = '[Daisyproducer] '

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Zurich'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'archive')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/archive/'

LOGIN_REDIRECT_URL = '/todo'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# URL prefix for static files.
STATIC_URL = '/media/'

# Format for date and datetime strings.
DATE_FORMAT = 'Y-m-d H:i'
DATETIME_FORMAT = 'j M y H:i'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '9jf6-plsfz1fy8x-%lgy+4gt9a)z1u4)!8e)aa%pg*z+i-+h6f'

# The maximum size (in bytes) that an upload will be before it gets
# streamed to the file system. Set this to 0 so that files are stored
# in a temporary location and can be validated by external tools. 
FILE_UPLOAD_MAX_MEMORY_SIZE = 0

# The path to the  the Daisy Pipeline 
DAISY_PIPELINE_PATH = os.path.join(PROJECT_DIR, '..', '..', 'tmp', 'pipeline-20090410')

# The publisher that should be inserted in the meta data by default
DAISY_DEFAULT_PUBLISHER = "SBS Schweizerische Bibliothek für Blinde, Seh- und Lesebehinderte"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

RESTRUCTUREDTEXT_FILTER_SETTINGS = {'doctitle_xform': 0}

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'daisyproducer.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR, 'templates')
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "daisyproducer.version.version_processor")

INSTALLED_APPS = (
    'daisyproducer.documents',
    'daisyproducer.dictionary',
    'daisyproducer.statistics',
    'daisyproducer.abacus_import',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'south',
)
