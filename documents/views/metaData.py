from daisyproducer.documents.models import Document, Version
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.db import transaction
from django.forms import ModelForm
from django.template.loader import render_to_string
from django.views.generic.create_update import create_object, update_object

class PartialDocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = ('title', 'author', 'publisher', 'assigned_to')

    def save(self):
        instance = super(PartialDocumentForm, self).save()
        if instance.version_set.count() == 0:
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
        return instance

@login_required
@transaction.commit_on_success
def create(request):
    response = create_object(
        request,
        form_class=PartialDocumentForm,
        post_save_redirect=reverse('manage_index'),
        login_required = True,
        template_name = 'documents/metaData_create.html',
    )
    return response

@login_required
@transaction.commit_on_success
def update(request, document_id):
    # Delegate to the generic view and get an HttpResponse.
    response = update_object(
        request,
        form_class=PartialDocumentForm,
        post_save_redirect=reverse('manage_index'),
        object_id = document_id,
        login_required = True,
        template_name = 'documents/metaData_update.html',
    )
    return response
