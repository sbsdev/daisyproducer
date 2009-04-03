from django.shortcuts import render_to_response, get_object_or_404
from daisyproducer.documents.models import Document, Version
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.forms import ModelForm

class PartialVersionForm(ModelForm):
    class Meta:
        model = Version
        fields = ('content',)

@login_required
def index(request):
    """Show all the documents that are relevant for the groups that
    the user has and group them by action
    """
    document_list = Document.objects.all().order_by('state','title')
    return render_to_response('documents/manage_index.html', locals())
    
@login_required
def detail(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method == 'POST':
        form = PartialVersionForm(request.POST, request.FILES)
        if form.is_valid():
            version = form.save(commit=False)
            version.document = document
            # FIXME: make sure the uploaded version is valid xml
            version.save()
            return HttpResponseRedirect("/manage/%s/" % document_id)

    versionForm = PartialVersionForm()
    return render_to_response('documents/manage_detail.html', locals())
    
@login_required
def transition(request, document_id, newState):
    document = Document.objects.get(pk=document_id)

    document.transitionTo(newState)
    return HttpResponseRedirect('/manage/')
