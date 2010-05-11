from daisyproducer.documents.external import DaisyPipeline, SBSForm
from daisyproducer.documents.forms import PartialDocumentForm, PartialVersionForm, PartialAttachmentForm, OCRForm, MarkupForm, SBSFormForm
from daisyproducer.documents.models import Document, Version, Attachment, LargePrintProfileForm
from daisyproducer.documents.views.utils import render_to_mimetype_response
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic.list_detail import object_list
from lxml import etree

@login_required
def index(request):
    """Show all the documents that are relevant for the groups that
    the user has and group them by action"""
    # FIXME: this can be simplified in a more modern version of django
    # (see http://docs.djangoproject.com/en/dev/ref/models/querysets/#in)
    # to the following: 
    # user_groups = request.user.groups
    user_groups = request.user.groups.values('pk').query
    response = object_list(
        request,
        queryset = Document.objects.select_related('state').filter(
            # only show documents that aren't assigned to anyone else,
            Q(assigned_to=request.user) | Q(assigned_to__isnull=True),
            # and which are in a state for which my group is responsible
            state__responsible__in=user_groups
            ).order_by('state','title'),
        template_name = 'documents/todo_index.html'
    )
    return response
    
@login_required
def detail(request, document_id):
    try:
        document = Document.objects.select_related('state').get(pk=document_id)
    except Document.DoesNotExist:
        raise Http404

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

    # this is a bit of a hack as we need to create (and save) an
    # attachment before the id is known. We need to know the id before we
    # can save the content file under /document_id/attachments/file_name
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
    # attach some data to the form for validation        
    from django.forms.models import model_to_dict
    form.contentMetaData = model_to_dict(document)

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
    return HttpResponseRedirect(reverse('todo_index'))

@login_required
def ocr(request, document_id):
    document = Document.objects.get(pk=document_id)
    if request.method == 'POST':
        form = OCRForm(request.POST, request.FILES)
        if form.is_valid():
            # do whatever is needed here
            return HttpResponseRedirect(reverse('todo_detail', args=[document_id]))
    else:
        form = OCRForm()

    return render_to_response('documents/todo_ocr.html', locals(),
                              context_instance=RequestContext(request))

@login_required
def markup(request, document_id):
    document = Document.objects.select_related('state').get(pk=document_id)
    if request.method == 'POST':
        form = MarkupForm(request.POST)
        if form.is_valid():
            # create a new version with the given form content
            form.save(document)
            return HttpResponseRedirect(reverse('todo_detail', args=[document_id]))
    else:
        file_field = document.latest_version().content
        file_field.open()
        content = file_field.read()
        file_field.close()
        form = MarkupForm({'data' : content, 'comment' : "Insert a comment here"})

    return render_to_response('documents/todo_markup.html', locals(),
                              context_instance=RequestContext(request))

@login_required
def markup_xopus(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    if request.method == 'POST':
        rawData = request.raw_post_data
        root = etree.fromstring(rawData)
#        root.getroottree().write("/tmp/document.xml", encoding="UTF-8", xml_declaration=True)    
        content = ContentFile(
            etree.tostring(root, 
                           encoding="UTF-8",
                           pretty_print=True,
                           xml_declaration=True))
        version = Version.objects.create(
            comment="Changed with Xopus", 
            document=document)
        version.content.save("initial_version.xml", content)
        return HttpResponse("success")
    else:
        return render_to_response('documents/todo_markup_xopus.html', locals(),
                                  context_instance=RequestContext(request))

@login_required
def preview_xhtml(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    inputFile = document.latest_version().content.path
    outputFile = "/tmp/%s.xhtml" % document_id
    params = {}
    DaisyPipeline.dtbook2xhtml(inputFile, outputFile, **params)

    return render_to_mimetype_response('text/html', 
                                       document.title.encode('utf-8'), outputFile)

@login_required
def preview_sbsform(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method == 'POST':
        form = SBSFormForm(request.POST)
        if form.is_valid():
            inputFile = document.latest_version().content.path
            outputFile = "/tmp/%s.sbsform" % document_id
            SBSForm.dtbook2sbsform(inputFile, outputFile, **form.cleaned_data)
            return render_to_mimetype_response('text/x-sbsform', 
                                               document.title.encode('utf-8'), outputFile)
    else:
        form = SBSFormForm()

    return render_to_response('documents/todo_sbsform.html', locals(),
                              context_instance=RequestContext(request))

@login_required
def preview_pdf(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method == 'POST':
        form = LargePrintProfileForm(request.POST)
        if form.is_valid():
            inputFile = document.latest_version().content.path
            outputFile = "/tmp/%s.pdf" % document_id
            DaisyPipeline.dtbook2pdf(inputFile, outputFile, **form.cleaned_data)
            return render_to_mimetype_response('application/pdf', 
                                               document.title.encode('utf-8'), outputFile)
    else:
        form = LargePrintProfileForm()

    return render_to_response('documents/todo_pdf.html', locals(),
                              context_instance=RequestContext(request))

