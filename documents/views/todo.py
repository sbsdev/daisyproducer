import shutil, tempfile, os.path

from daisyproducer.documents.external import DaisyPipeline, SBSForm, StandardLargePrint, zipDirectory
from daisyproducer.documents.forms import PartialDocumentForm, PartialVersionForm, PartialAttachmentForm, OCRForm, MarkupForm, SBSFormForm, RTFForm, EPUBForm, TextOnlyDTBForm, DTBForm, SalePDFForm
from daisyproducer.documents.models import Document, Version, Attachment, LargePrintProfileForm
from daisyproducer.documents.views.utils import render_to_mimetype_response
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic.list_detail import object_list


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
        mime_type=form.content_type,
        created_by=request.user)
    content_file = request.FILES['content']
    attachment.content.save(content_file.name, content_file)

    return HttpResponseRedirect(reverse('todo_detail', args=[document_id]))
    
@login_required
@transaction.commit_on_success
def add_version(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method != 'POST':
        return HttpResponseRedirect(reverse('todo_detail', args=[document_id]))

    form = PartialVersionForm(request.POST, request.FILES, 
                              contentMetaData=model_to_dict(document))
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
        document=document,
        created_by=request.user)
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
        form = MarkupForm(request.POST, 
                          document=document, user=request.user)
        if form.is_valid():
            # create a new version with the given form content
            form.save()
            return HttpResponseRedirect(reverse('todo_detail', args=[document_id]))
        else:
            form.has_errors = True
    else:
        file_field = document.latest_version().content
        file_field.open()
        content = file_field.read()
        file_field.close()
        form = MarkupForm({'data' : content, 'comment' : "Insert a comment here"})
        # This is a bit of a cheap hack to avoid expensive validation
        # on initial display of the form
        form.has_errors = False

    return render_to_response('documents/todo_markup.html', locals(),
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
            SBSForm.dtbook2sbsform(inputFile, outputFile, 
                                   document_identifier=document.identifier,
                                   use_local_dictionary=document.has_local_words(), 
                                   **form.cleaned_data)
            contraction = form.cleaned_data['contraction']
            contraction_to_mimetype_mapping = {0 : 'text/x-sbsform-g0', 
                                               1 : 'text/x-sbsform-g1',
                                               2 : 'text/x-sbsform-g2'}
            mimetype = contraction_to_mimetype_mapping.get(contraction, 'text/x-sbsform-g2')
            return render_to_mimetype_response(mimetype, document.title.encode('utf-8'), outputFile)
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

@login_required
def preview_library_pdf(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    inputFile = document.latest_version().content.path
    outputFile = "/tmp/%s.pdf" % document_id
    StandardLargePrint.dtbook2pdf(inputFile, outputFile)
    filename = document.title + u" 17pt"
    return render_to_mimetype_response('application/pdf', filename.encode('utf-8'), outputFile)


@login_required
def preview_sale_pdf(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method == 'POST':
        form = SalePDFForm(request.POST)
        if form.is_valid():
            inputFile = document.latest_version().content.path
            outputFile = "/tmp/%s.pdf" % document_id
            StandardLargePrint.dtbook2pdf(inputFile, outputFile, **form.cleaned_data)
            filename = document.title + u" " + form.cleaned_data['font_size']
            return render_to_mimetype_response('application/pdf', 
                                               filename.encode('utf-8'), outputFile)
    else:
        form = SalePDFForm()

    return render_to_response('documents/todo_sale_pdf.html', locals(),
                              context_instance=RequestContext(request))

@login_required
def preview_rtf(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method == 'POST':
        form = RTFForm(request.POST)
        if form.is_valid():
            inputFile = document.latest_version().content.path
            outputFile = "/tmp/%s.rtf" % document_id
            DaisyPipeline.dtbook2rtf(inputFile, outputFile, **form.cleaned_data)
            return render_to_mimetype_response('application/rtf', 
                                               document.title.encode('utf-8'), outputFile)
    else:
        form = RTFForm()

    return render_to_response('documents/todo_rtf.html', locals(),
                              context_instance=RequestContext(request))

@login_required
def preview_epub(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method == 'POST':
        form = EPUBForm(request.POST)
        if form.is_valid():
            inputFile = document.latest_version().content.path
            outputFile = "/tmp/%s.epub" % document_id
            defaults = {
                "dctitle" : document.title, 
                "dcidentifier" : document.identifier, 
                "dclanguage" : document.language, 
                "dccreator" : document.author, 
                "dcpublisher" : document.publisher, 
                "dcdate" : document.date}
            defaults.update(form.cleaned_data)
            DaisyPipeline.dtbook2epub(inputFile, outputFile, **defaults)
            return render_to_mimetype_response('application/epub+zip', 
                                               document.title.encode('utf-8'), outputFile)
    else:
        form = EPUBForm()

    return render_to_response('documents/todo_epub.html', locals(),
                              context_instance=RequestContext(request))

@login_required
def preview_text_only_dtb(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method == 'POST':
        form = TextOnlyDTBForm(request.POST)
        if form.is_valid():
            inputFile = document.latest_version().content.path
            outputDir = tempfile.mkdtemp(prefix="daisyproducer-")

            transformationErrors = DaisyPipeline.dtbook2text_only_dtb(inputFile, outputDir, **form.cleaned_data)
            if transformationErrors:
                return render_to_response('documents/todo_text_only_dtb.html', locals(),
                                          context_instance=RequestContext(request))

            zipFile = tempfile.NamedTemporaryFile(suffix='.zip', prefix=document_id, delete=False)
            zipDirectory(outputDir, zipFile.name, document.title)
            shutil.rmtree(outputDir)
    
            return render_to_mimetype_response('application/zip', 
                                               document.title.encode('utf-8'), zipFile.name)
    else:
        form = TextOnlyDTBForm()

    return render_to_response('documents/todo_text_only_dtb.html', locals(),
                              context_instance=RequestContext(request))

@login_required
def preview_dtb(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method == 'POST':
        form = DTBForm(request.POST)
        if form.is_valid():
            inputFile = document.latest_version().content.path
            outputDir = tempfile.mkdtemp(prefix="daisyproducer-")
            DaisyPipeline.dtbook2dtb(inputFile, outputDir, **form.cleaned_data)

            zipFile = tempfile.NamedTemporaryFile(suffix='.zip', prefix=document_id, delete=False)
            zipDirectory(outputDir, zipFile.name, document.title)
            shutil.rmtree(outputDir)

            return render_to_mimetype_response('application/zip', 
                                               document.title.encode('utf-8'), zipFile.name)
    else:
        form = DTBForm()

    return render_to_response('documents/todo_dtb.html', locals(),
                              context_instance=RequestContext(request))

