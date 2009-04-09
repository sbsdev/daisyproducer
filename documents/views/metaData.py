from daisyproducer.documents.models import Document
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm
from django.core.urlresolvers import reverse
from django.views.generic.create_update import create_object, update_object

class PartialDocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = ('title', 'author', 'publisher')

@login_required
def create(request):
    response = create_object(
        request,
        form_class=PartialDocumentForm,
        post_save_redirect=reverse('manage_index'),
        login_required = True,
        template_name = 'documents/metaData_update.html',
    )
    return response

@login_required
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
