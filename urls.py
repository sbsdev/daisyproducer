from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout

import os.path
PROJECT_DIR = os.path.dirname(__file__)

from django.contrib import admin
admin.autodiscover()

# browse finished documents
urlpatterns = patterns('daisyproducer.documents.views.browse',
    url(r'^$', 'index', name='browse_index'),
    url(r'^(?P<document_id>\d+)/$', 'detail', name='browse_detail'),

    url(r'^(?P<document_id>\d+).pdf$', 'as_pdf', name='browse_pdf'),
    url(r'^(?P<document_id>\d+).brl$', 'as_brl', name='browse_brl'),
)

# work on pending documents
urlpatterns += patterns('daisyproducer.documents.views.todo',
    url(r'^todo/$', 'index', name='todo_index'),
    url(r'^todo/(?P<document_id>\d+)/$', 'detail', name='todo_detail'),
    url(r'^todo/(?P<document_id>\d+)/addVersion$', 'add_version', name='todo_add_version'),
    url(r'^todo/(?P<document_id>\d+)/addAttachment$', 'add_attachment', name='todo_add_attachment'),
    url(r'^todo/(?P<document_id>\d+)/transition$', 'transition', name='todo_transition'),
)

# meta data
urlpatterns += patterns('daisyproducer.documents.views.metaData',
    url(r'^metadata/$', 'index', name='meta_index'),
    url(r'^metadata/(?P<document_id>\d+)/$', 'detail', name='meta_detail'),
    url(r'^metadata/create/$', 'create', name='meta_create'),
    url(r'^metadata/(?P<document_id>\d+)/edit/$', 'edit', name='meta_edit'),
)

urlpatterns += patterns('',
    # authentication
    (r'^accounts/login/$',  login, {'template_name' : 'login.html'}),
    (r'^accounts/logout/$', logout),

    # static files
    (r'^stylesheets/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': os.path.join(PROJECT_DIR, 'public', 'stylesheets')}),
    (r'^javascripts/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': os.path.join(PROJECT_DIR, 'public', 'javascripts')}),
    (r'^archive/(?P<path>.*)$', 'django.views.static.serve',
     {'document_root': os.path.join(PROJECT_DIR, 'archive')}),

    # enable the admin:
    (r'^admin/(.*)', admin.site.root),
)
