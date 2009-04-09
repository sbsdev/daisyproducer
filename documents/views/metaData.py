from django.shortcuts import render_to_response
from daisyproducer.documents.models import Document
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm
from django.core.urlresolvers import reverse
from django.views.generic.create_update import update_object

class PartialDocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = ('title', 'author', 'publisher')

@login_required
def create(request):
    documentForm = PartialDocumentForm()
    if request.method == "POST":
        documentForm = PartialDocumentForm(request.POST)
        if documentForm.is_valid():
            documentForm.save()
            return HttpResponseRedirect(reverse('manage_index'))
    
    return render_to_response('documents/metaData_create.html', locals())

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
