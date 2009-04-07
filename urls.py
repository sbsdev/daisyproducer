from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout

import os.path
PROJECT_DIR = os.path.dirname(__file__)

from django.contrib import admin
admin.autodiscover()

# consume
urlpatterns = patterns('daisyproducer.documents.views.consume',
    url(r'^documents/$', 'index', name='consume_index'),
    url(r'^documents/(?P<document_id>\d+)/$', 'detail', name='consume_detail'),

    url(r'^documents/(?P<document_id>\d+).pdf$', 'as_pdf'),
    url(r'^documents/(?P<document_id>\d+).brl$', 'as_brl'),
)

# manage
urlpatterns += patterns('daisyproducer.documents.views.manage',
    url(r'^manage/$', 'index', name='manage_index'),
    url(r'^manage/(?P<document_id>\d+)/$', 'detail', name='manage_detail'),
    url(r'^manage/(?P<document_id>\d+)/addVersion$', 'add_version', name='manage_add_version'),
    url(r'^manage/(?P<document_id>\d+)/addAttachment$', 'add_attachment', name='manage_add_attachmentdetail'),
    url(r'^manage/(?P<document_id>\d+)/transition$', 'transition', name='manage_transition'),
)

# meta data
urlpatterns += patterns('daisyproducer.documents.views.metaData',
    url(r'^documents/create/$', 'create', name='meta_create'),
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
