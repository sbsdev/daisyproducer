import os.path

from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.utils.translation import ugettext_lazy as _


PROJECT_DIR = os.path.dirname(__file__)

admin.autodiscover()

# browse finished documents
urlpatterns = patterns('daisyproducer.documents.views.browse',
    url(r'^$', 'index', name='browse_index'),
    url(r'^(?P<document_id>\d+)/$', 'detail', name='browse_detail'),

    url(r'^(?P<document_id>\d+).pdf$', 'as_pdf', name='browse_pdf'),
    url(r'^(?P<document_id>\d+).brl$', 'as_brl', name='browse_brl'),
    url(r'^(?P<document_id>\d+).sbsform$', 'as_sbsform', name='browse_sbsform'),
    url(r'^(?P<document_id>\d+).xhtml$', 'as_xhtml', name='browse_xhtml'),
    url(r'^(?P<document_id>\d+).rtf$', 'as_rtf', name='browse_rtf'),
    url(r'^(?P<document_id>\d+).epub$', 'as_epub', name='browse_epub'),
    url(r'^(?P<document_id>\d+).text_only_fileset$', 'as_text_only_fileset', name='browse_text_only_fileset'),
    url(r'^(?P<document_id>\d+).dtb$', 'as_dtb', name='browse_dtb'),
)

# work on pending documents
urlpatterns += patterns('daisyproducer.documents.views.todo',
    url(r'^todo/$', 'index', name='todo_index'),
    url(r'^todo/(?P<document_id>\d+)/$', 'detail', name='todo_detail'),
    url(r'^todo/(?P<document_id>\d+)/addVersion$', 'add_version', name='todo_add_version'),
    url(r'^todo/(?P<document_id>\d+)/addAttachment$', 'add_attachment', name='todo_add_attachment'),
    url(r'^todo/(?P<document_id>\d+)/transition$', 'transition', name='todo_transition'),
    url(r'^todo/(?P<document_id>\d+)/ocr$', 'ocr', name='todo_ocr'),
    url(r'^todo/(?P<document_id>\d+)/markup$', 'markup', name='todo_markup'),
    url(r'^todo/(?P<document_id>\d+)/markup_xopus$', 'markup_xopus', name='todo_markup_xopus'),
    url(r'^todo/(?P<document_id>\d+)/preview_xhtml$', 'preview_xhtml', name='todo_xhtml'),
    url(r'^todo/(?P<document_id>\d+)/preview_sbsform$', 'preview_sbsform', name='todo_sbsform'),
    url(r'^todo/(?P<document_id>\d+)/preview_pdf$', 'preview_pdf', name='todo_pdf'),
)

# management of documents and meta data
urlpatterns += patterns('daisyproducer.documents.views.manage',
    url(r'^manage/$', 'index', name='manage_index'),
    url(r'^manage/(?P<document_id>\d+)/$', 'detail', name='manage_detail'),
    url(r'^manage/create/$', 'create', name='manage_create'),
    url(r'^manage/(?P<document_id>\d+)/update/$', 'update', name='manage_update'),
)

# help and about
def getRSTContent(file_name):
    f = open(os.path.join(PROJECT_DIR, 'doc', 'help', file_name))
    return f.read()

urlpatterns += patterns('',
    # help
    url(r'^help/$', 'django.views.generic.simple.direct_to_template', 
        {'template': 'help.html',
         'extra_context': {
                'content': getRSTContent('index.txt'),
                'title': _('Help')}},
        "help"),
    # about
    url(r'^about/$', 'django.views.generic.simple.direct_to_template', 
        {'template': 'help.html',
         'extra_context': {
                'content': getRSTContent('about.txt'),
                'title': _('About')}},
        "about"),
)

# authentication
urlpatterns += patterns('',
    (r'^accounts/login/$',  login, {'template_name' : 'login.html'}),
    (r'^accounts/logout/$', logout),
)

# enable the admin:
urlpatterns += patterns('',
    (r'^admin/(.*)', admin.site.root),
)

# static files
if settings.SERVE_STATIC_FILES:
    urlpatterns += patterns('',
        (r'^stylesheets/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': os.path.join(PROJECT_DIR, 'public', 'stylesheets')}),
        (r'^javascripts/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': os.path.join(PROJECT_DIR, 'public', 'javascripts')}),
        (r'^archive/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': os.path.join(PROJECT_DIR, 'archive')}),
        (r'^images/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': os.path.join(PROJECT_DIR, 'public', 'images')}),
        (r'^xopus/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': os.path.join(PROJECT_DIR, 'public', 'xopus')}),
        (r'^xopus-local/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': os.path.join(PROJECT_DIR, 'public', 'xopus-local')}),
    )

