from daisyproducer.documents.models import Document, Version
from daisyproducer.documents.versionContent import VersionContent
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.db import transaction
from django.forms import ModelForm
from django.template.loader import render_to_string
from django.views.generic.create_update import create_object, update_object
from django.views.generic.list_detail import object_list, object_detail

@login_required
def index(request):
    response = object_list(
        request,
        queryset = Document.objects.all().order_by('state','title'),
        template_name = 'documents/manage_index.html',
    )
    return response
    
@login_required
def detail(request, document_id):
    response = object_detail(
        request,
        queryset = Document.objects.all(),
        template_name = 'documents/manage_detail.html',
        object_id = document_id,
    )
    return response

class PartialDocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = ('title', 'author', 'publisher', 'assigned_to')

    def save(self):
        instance = super(PartialDocumentForm, self).save()
        if instance.version_set.count() == 0:
            # create an initial version
            contentString  = render_to_string('DTBookTemplate.xml', {
                    'title' : self.cleaned_data['title'],
                    'author' : self.cleaned_data['author'],
                    'publisher' : self.cleaned_data['publisher'],
                    })
            content = ContentFile(contentString)
            version = Version.objects.create(
                comment = "Initial version created from meta data",
                document = instance)
            version.content.save("initial_version.xml", content)
        else:
            # create a new version with the new content
            version = instance.latest_version()
            versionContent = VersionContent(version)
            contentString = versionContent.getUpdatedContent(**self.cleaned_data)
            content = ContentFile(contentString)
            version = Version.objects.create(
                comment = "Updated version due to meta data change",
                document = instance)
            version.content.save("updated_version.xml", content)
        return instance

@login_required
@transaction.commit_on_success
def create(request):
    response = create_object(
        request,
        form_class=PartialDocumentForm,
        post_save_redirect=reverse('todo_index'),
        login_required = True,
        template_name = 'documents/manage_create.html',
    )
    return response

@login_required
@transaction.commit_on_success
def edit(request, document_id):
    # Delegate to the generic view and get an HttpResponse.
    response = update_object(
        request,
        form_class=PartialDocumentForm,
        post_save_redirect=reverse('manage_index'),
        object_id = document_id,
        login_required = True,
        template_name = 'documents/manage_update.html',
    )
    return response
