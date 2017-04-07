import os
import sys

path_to_daisyproducer = os.path.dirname(os.path.dirname(__file__))
sys.path.append(path_to_daisyproducer) 

os.environ['DJANGO_SETTINGS_MODULE'] = 'daisyproducer.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
