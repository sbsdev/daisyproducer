from daisyproducer.documents.forms import PartialDocumentForm, PartialVersionForm, PartialAttachmentForm
from daisyproducer.documents.models import Document, Version, Attachment
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic.list_detail import object_list

@login_required
def index(request):
    """Show all the documents that are relevant for the groups that
    the user has and group them by action"""
    response = object_list(
        request,
        queryset = Document.objects.exclude(state__name='approved').order_by('state','title'),
        template_name = 'documents/todo_index.html',
    )
    return response
    
@login_required
def detail(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    versionForm = PartialVersionForm()
    attachmentForm = PartialAttachmentForm()
    documentForm = PartialDocumentForm()
    documentForm.limitChoicesToValidStates(document)
    return render_to_response('documents/todo_detail.html', locals(),
                              context_instance=RequestContext(request))

@login_required
@transaction.commit_on_success
def add_attachment(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method != 'POST':
        return HttpResponseRedirect(reverse('todo_detail', args=[document_id]))

    form = PartialAttachmentForm(request.POST, request.FILES)
    if not form.is_valid():
        versionForm = PartialVersionForm()
        attachmentForm = form
        documentForm = PartialDocumentForm()
        documentForm.limitChoicesToValidStates(document)
        return render_to_response('documents/todo_detail.html', locals(),
                                  context_instance=RequestContext(request))

    # this is a bit of a hack as we need to create (and save) a
    # version before the id is known. We need to know the id before we
    # can save the content file under /document_id/versions/version_id
    attachment = Attachment.objects.create(
        comment=form.cleaned_data['comment'], 
        document=document,
        mime_type=form.content_type)
    content_file = request.FILES['content']
    attachment.content.save(content_file.name, content_file)

    return HttpResponseRedirect(reverse('todo_detail', args=[document_id]))
    
@login_required
@transaction.commit_on_success
def add_version(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method != 'POST':
        return HttpResponseRedirect(reverse('todo_detail', args=[document_id]))

    form = PartialVersionForm(request.POST, request.FILES)
    if not form.is_valid():
        versionForm = form
        attachmentForm = PartialAttachmentForm()
        documentForm = PartialDocumentForm()
        documentForm.limitChoicesToValidStates(document)
        return render_to_response('documents/todo_detail.html', locals(),
                                  context_instance=RequestContext(request))

    # this is a bit of a hack as we need to create (and save) a
    # version before the id is known. We need to know the id before we
    # can save the content file under /document_id/versions/version_id
    version = Version.objects.create(
        comment=form.cleaned_data['comment'], 
        document=document)
    content_file = request.FILES['content']
    version.content.save(content_file.name, content_file)

    return HttpResponseRedirect(reverse('todo_detail', args=[document_id]))

@login_required
def transition(request, document_id):
    document = Document.objects.get(pk=document_id)

    if request.method != 'POST':
        return HttpResponseRedirect(reverse('todo_detail', args=[document_id]))

    form = PartialDocumentForm(request.POST)
    if not form.is_valid():
        versionForm = PartialVersionForm()
        attachmentForm = PartialAttachmentForm()
        documentForm = form
        return render_to_response('documents/todo_detail.html', locals(),
                                  context_instance=RequestContext(request))

    document.transitionTo(form.cleaned_data['state'])
    return HttpResponseRedirect(reverse('todo_detail', args=[document_id]))