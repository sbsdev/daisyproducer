from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^documents/$', 'daisyproducer.documents.views.index'),
    (r'^documents/(?P<document_id>\d+)/$', 'daisyproducer.documents.views.detail'),

    (r'^documents/(?P<document_id>\d+).pdf$', 'daisyproducer.documents.views.as_pdf'),
    (r'^documents/(?P<document_id>\d+).brl$', 'daisyproducer.documents.views.as_brl'),

    # static files
    (r'^stylesheets/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/eglic/src/daisyproducer/media'}),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
)
