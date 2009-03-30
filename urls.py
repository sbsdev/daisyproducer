from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout

import os.path
PROJECT_DIR = os.path.dirname(__file__)

from django.contrib import admin
admin.autodiscover()

# consume
urlpatterns = patterns('daisyproducer.documents.views',
    (r'^documents/$', 'index'),
    (r'^documents/(?P<document_id>\d+)/$', 'detail'),

    (r'^documents/(?P<document_id>\d+).pdf$', 'as_pdf'),
    (r'^documents/(?P<document_id>\d+).brl$', 'as_brl'),
)

# manage
urlpatterns += patterns('daisyproducer.documents.manageViews',
    (r'^manage/$', 'index'),
    (r'^manage/(?P<document_id>\d+)/$', 'detail'),
    (r'^manage/(?P<document_id>\d+)/done$', 'done'),
)

# create
urlpatterns += patterns('daisyproducer.documents.createViews',
    (r'^documents/create/$', 'create'),
)

urlpatterns += patterns('',
    # authentication
    (r'^accounts/login/$',  login, {'template_name' : 'login.html'}),
    (r'^accounts/logout/$', logout),

    # static files
    (r'^stylesheets/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': os.path.join(PROJECT_DIR, 'media')}),

    # enable the admin:
    (r'^admin/(.*)', admin.site.root),
)
