import os.path

import django
from django.conf import settings
from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView

import daisyproducer.documents.views.manage as manage
import daisyproducer.documents.views.browse as browse
import daisyproducer.documents.views.todo as todo

PROJECT_DIR = os.path.dirname(__file__)

admin.autodiscover()

# browse finished documents
urlpatterns = patterns('daisyproducer.documents.views.browse',
    url(r'^$', browse.BrowseListView.as_view(), name='browse_index'),
    url(r'^(?P<pk>\d+)/$', browse.BrowseDetailView.as_view(), name='browse_detail'),
    url(r'^(?P<document_id>\d+).pdf$', browse.as_pdf, name='browse_pdf'),
    url(r'^(?P<document_id>\d+).brl$', browse.as_brl, name='browse_brl'),
    url(r'^(?P<document_id>\d+).sbsform$', browse.as_sbsform, name='browse_sbsform'),
    url(r'^(?P<document_id>\d+).xhtml$', browse.as_xhtml, name='browse_xhtml'),
    url(r'^(?P<document_id>\d+).rtf$', browse.as_rtf, name='browse_rtf'),
    url(r'^(?P<document_id>\d+).epub$', browse.as_epub, name='browse_epub'),
    url(r'^(?P<document_id>\d+).dtb_text_only$', browse.as_text_only_dtb, name='browse_text_only_dtb'),
    url(r'^(?P<document_id>\d+).dtb$', browse.as_dtb, name='browse_dtb'),
)

# work on pending documents
urlpatterns += patterns('daisyproducer.documents.views.todo',
    url(r'^todo/$', todo.TodoListView.as_view(), name='todo_index'),
    url(r'^todo/(?P<document_id>\d+)/$', todo.detail, name='todo_detail'),
    url(r'^todo/(?P<document_id>\d+)/addVersion$', todo.add_version, name='todo_add_version'),
    url(r'^todo/(?P<document_id>\d+)/addImage$', todo.add_image, name='todo_add_image'),
    url(r'^todo/(?P<document_id>\d+)/addAttachment$', todo.add_attachment, name='todo_add_attachment'),
    url(r'^todo/(?P<document_id>\d+)/transition$', todo.transition, name='todo_transition'),
    url(r'^todo/(?P<document_id>\d+)/markup$', todo.markup, name='todo_markup'),
    url(r'^todo/(?P<document_id>\d+)/preview_xhtml$', todo.preview_xhtml, name='todo_xhtml'),
    url(r'^todo/(?P<document_id>\d+)/preview_sbsform$', todo.preview_sbsform, name='todo_sbsform'),
    url(r'^todo/(?P<document_id>\d+)/preview_sbsform_new$', todo.preview_sbsform_new, name='todo_sbsform_new'),
    url(r'^todo/(?P<document_id>\d+)/preview_pdf$', todo.preview_pdf, name='todo_pdf'),
    url(r'^todo/(?P<document_id>\d+)/preview_sale_pdf$', todo.preview_sale_pdf, name='todo_sale_pdf'),
    url(r'^todo/(?P<document_id>\d+)/preview_library_pdf$', todo.preview_library_pdf, name='todo_library_pdf'),
    url(r'^todo/(?P<document_id>\d+)/preview_rtf$', todo.preview_rtf, name='todo_rtf'),
    url(r'^todo/(?P<document_id>\d+)/preview_epub$', todo.preview_epub, name='todo_epub'),
    url(r'^todo/(?P<document_id>\d+)/preview_odt$', todo.preview_odt, name='todo_odt'),
    url(r'^todo/(?P<document_id>\d+)/preview_text_only_dtb$', todo.preview_text_only_dtb, name='todo_text_only_dtb'),
    url(r'^todo/(?P<document_id>\d+)/preview_dtb$', todo.preview_dtb, name='todo_dtb'),
)

# management of documents and meta data
urlpatterns += patterns('daisyproducer.documents.views.manage',
    url(r'^manage/$', manage.ManageListView.as_view(), name='manage_index'),
    url(r'^manage/(?P<pk>\d+)/$', manage.ManageDetailView.as_view(), name='manage_detail'),
    url(r'^manage/create/$', manage.create, name='manage_create'),
    url(r'^manage/(?P<document_id>\d+)/update/$', manage.update, name='manage_update'),
    url(r'^manage/upload_metadata_csv/$', manage.upload_metadata_csv, name='upload_metadata_csv'),
    url(r'^manage/import_metadata_csv/$', manage.import_metadata_csv, name='import_metadata_csv'),
)

urlpatterns += patterns('daisyproducer.statistics.views',
    # statistics
    url(r'^manage/stats/$', 'index', name='stats_index'),
    url(r'^manage/stats/csv$', 'all_data_as_csv', name='all_data_as_csv'),
)

# work on dictionary
urlpatterns += patterns('daisyproducer.dictionary.views',
    url(r'^todo/(?P<document_id>\d+)/check_words_g1$', 'check', kwargs={'grade': 1}, name='dictionary_check_g1'),
    url(r'^todo/(?P<document_id>\d+)/check_words_g2$', 'check', kwargs={'grade': 2}, name='dictionary_check_g2'),
    url(r'^todo/(?P<document_id>\d+)/local_words_g1$', 'local', kwargs={'grade': 1}, name='dictionary_local_g1'),
    url(r'^todo/(?P<document_id>\d+)/local_words_g2$', 'local', kwargs={'grade': 2}, name='dictionary_local_g2'),
    url(r'^todo/confirm_words_g1$', 'confirm', kwargs={'grade': 1}, name='dictionary_confirm_g1'),
    url(r'^todo/confirm_words_g2$', 'confirm', kwargs={'grade': 2}, name='dictionary_confirm_g2'),
    url(r'^todo/confirm_deferred_words_g1$', 'confirm', kwargs={'grade': 1, 'deferred': True}, name='dictionary_confirm_deferred_g1'),
    url(r'^todo/confirm_deferred_words_g2$', 'confirm', kwargs={'grade': 2, 'deferred': True}, name='dictionary_confirm_deferred_g2'),
    url(r'^todo/confirm_single_word_g1$', 'confirm_single', kwargs={'grade': 1}, name='dictionary_single_confirm_g1'),
    url(r'^todo/confirm_single_word_g2$', 'confirm_single', kwargs={'grade': 2}, name='dictionary_single_confirm_g2'),
    url(r'^todo/confirm_single_deferred_word_g1$', 'confirm_single', kwargs={'grade': 1, 'deferred': True}, name='dictionary_single_confirm_deferred_g1'),
    url(r'^todo/confirm_single_deferred_word_g2$', 'confirm_single', kwargs={'grade': 2, 'deferred': True}, name='dictionary_single_confirm_deferred_g2'),
    url(r'^todo/confirm_conflicting_duplicates_g1$', 'confirm_conflicting_duplicates', kwargs={'grade': 1},
        name='dictionary_confirm_conflicting_duplicates_g1'),
    url(r'^todo/confirm_conflicting_duplicates_g2$', 'confirm_conflicting_duplicates', kwargs={'grade': 2}, 
        name='dictionary_confirm_conflicting_duplicates_g2'),
    url(r'^todo/confirm_deferred_conflicting_duplicates_g1$', 'confirm_conflicting_duplicates', kwargs={'grade': 1, 'deferred': True},
        name='dictionary_confirm_deferred_conflicting_duplicates_g1'),
    url(r'^todo/confirm_deferred_conflicting_duplicates_g2$', 'confirm_conflicting_duplicates', kwargs={'grade': 2, 'deferred': True}, 
        name='dictionary_confirm_deferred_conflicting_duplicates_g2'),
    url(r'^todo/edit_global_words$', 'edit_global_words', kwargs={'read_only': False}, name='dictionary_edit_global_words'),
    url(r'^todo/lookup_global_words$', 'edit_global_words', kwargs={'read_only': True}, name='dictionary_lookup_global_words'),
    url(r'^todo/edit_missing_global_words$', 'edit_global_words_with_missing_braille', name='dictionary_edit_global_words_with_missing_braille'),
    url(r'^todo/export_words$', 'export_words', name='dictionary_export'),
    url(r'^todo/export_global_words_with_wrong_default_translation$', 'words_with_wrong_default_translation', name='dictionary_words_with_wrong_default_translation'),
)

# help and about
def getRSTContent(file_name):
    f = open(os.path.join(PROJECT_DIR, 'doc', 'help', file_name))
    return f.read()

class HelpView(TemplateView):
    template_name = "help.html"
    def get_context_data(self, **kwargs):
        context = super(HelpView, self).get_context_data(**kwargs)
        context.update({
            'content': getRSTContent('index.txt'),
            'title': _('Help')
        })
        return context

class AboutView(HelpView):
    def get_context_data(self, **kwargs):
        context = super(AboutView, self).get_context_data(**kwargs)
        context.update({
            'content': getRSTContent('about.txt'),
            'title': _('About')
        })
        return context


urlpatterns += patterns('',
    # help
    url(r'^help/$', HelpView.as_view(), name="help"),
    # about
    url(r'^about/$', AboutView.as_view(), name="about"),
)

# error
# FIXME: tbh I'm not sure if this ever worked
#urlpatterns += patterns('', url(r'^error/$', 'error', name='error'))

# authentication
urlpatterns += patterns('',
    url(r'^accounts/login/$',  login, {'template_name' : 'login.html'}, name='login'),
    url(r'^accounts/logout/$', logout, name="logout"),
)

# enable the admin:
if django.VERSION < (1, 3, 0, 'final', 0):
    urlpatterns += patterns('', (r'^admin/(.*)', admin.site.root),)
else:
    urlpatterns += patterns('', url(r'^admin/', include(admin.site.urls)),)

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
    )

