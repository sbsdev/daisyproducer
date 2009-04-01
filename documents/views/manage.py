from django.shortcuts import render_to_response, get_object_or_404
from daisyproducer.documents.models import Document, STATE_TRANSITION_MAP
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

@login_required
def index(request):
    """Show all the documents that are relevant for the groups that
    the user has and group them by action
    """
    document_list = Document.objects.all()
    document_list_by_state = {}
    for document in document_list:
        document_list_by_state.setdefault(document.state, []).append(document)
    document_list_by_transition = {}
    for state, documents in document_list_by_state.items():
        document_list_by_transition[STATE_TRANSITION_MAP[state]] = sorted(documents, lambda x,y: cmp(x.title, y.title))
    return render_to_response('documents/manage_index.html', locals())
    
@login_required
def detail(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    return render_to_response('documents/manage_detail.html', locals())
    
@login_required
def done(request, document_id):
    document = Document.objects.get(pk=document_id)
    # move to the next state and save
    # document.scan()
    # document.save()
    return HttpResponseRedirect('/manage/')
    
