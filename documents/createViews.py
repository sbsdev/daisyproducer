from django.shortcuts import render_to_response
from daisyproducer.documents.models import Document
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm

class PartialDocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = ('title', 'author', 'publisher')

@login_required
def create(request):
    documentForm = PartialDocumentForm()
    if request.method == "POST":
        documentForm = PartialDocumentForm(request.POST, request.FILES)
        if documentForm.is_valid():
            documentForm.save()
            return HttpResponseRedirect('/documents/')
    
    return render_to_response('documents/create.html', locals())

