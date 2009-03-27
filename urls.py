from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout

import os.path
PROJECT_DIR = os.path.dirname(__file__)

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^documents/$', 'daisyproducer.documents.views.index'),
    (r'^documents/(?P<document_id>\d+)/$', 'daisyproducer.documents.views.detail'),

    (r'^documents/(?P<document_id>\d+).pdf$', 'daisyproducer.documents.views.as_pdf'),
    (r'^documents/(?P<document_id>\d+).brl$', 'daisyproducer.documents.views.as_brl'),
    # manage
    (r'^manage/$', 'daisyproducer.documents.manageViews.index'),
    (r'^manage/(?P<document_id>\d+)/$', 'daisyproducer.documents.manageViews.detail'),
    (r'^manage/(?P<document_id>\d+)/done$', 'daisyproducer.documents.manageViews.done'),
    # create
    (r'^documents/create/$', 'daisyproducer.documents.createViews.create'),

    # authentication
    (r'^accounts/login/$',  login, {'template_name' : 'login.html'}),
    (r'^accounts/logout/$', logout),

    # static files
    (r'^stylesheets/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': os.path.join(PROJECT_DIR, 'media')}),

    # enable the admin:
    (r'^admin/(.*)', admin.site.root),
)
