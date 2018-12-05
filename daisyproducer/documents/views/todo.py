import shutil, tempfile, os.path

from daisyproducer.documents.external import DaisyPipeline, SBSForm, StandardLargePrint, zipDirectory, Pipeline2
from daisyproducer.documents.forms import PartialDocumentForm, PartialVersionForm, PartialAttachmentForm, PartialImageForm, MarkupForm, SBSFormForm, RTFForm, EPUBForm, EPUB3Form, DTBForm, SalePDFForm, ODTForm
from daisyproducer.documents.models import Document, Version, Attachment, Image, Product, LargePrintProfileForm
from daisyproducer.documents.views.utils import render_to_mimetype_response
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.views.generic.list import ListView

class TodoListView(ListView):
    template_name = 'documents/todo_index.html'

    def get_queryset(self):
        user_groups = self.request.user.groups.all()
        queryset = Document.objects.select_related('state').filter(
            # only show documents that aren't assigned to anyone else,
            Q(assigned_to=self.request.user) | Q(assigned_to__isnull=True),
            # and which are in a state for which my group is responsible
            state__responsible__in=user_groups
        ).order_by('state','title')
        return queryset

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(TodoListView, self).dispatch(request, *args, **kwargs)

@login_required
def detail(request, document_id):
    try:
        document = Document.objects.select_related('state').get(pk=document_id)
    except Document.DoesNotExist:
        raise Http404

    versionForm = PartialVersionForm()
    attachmentForm = PartialAttachmentForm()
    imageForm = PartialImageForm()
    documentForm = PartialDocumentForm()
    documentForm.limitChoicesToValidStates(document)
    return render(request, 'documents/todo_detail.html', locals())

@login_required
@transaction.atomic
def add_attachment(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method != 'POST':
        return HttpResponseRedirect(reverse('todo_detail', args=[document_id]))

    form = PartialAttachmentForm(request.POST, request.FILES)
    if not form.is_valid():
        versionForm = PartialVersionForm()
        attachmentForm = form
        imageForm = PartialImageForm()
        documentForm = PartialDocumentForm()
        documentForm.limitChoicesToValidStates(document)
        return render(request, 'documents/todo_detail.html', locals())

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
@transaction.atomic
def add_image(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method != 'POST':
        return HttpResponseRedirect(reverse('todo_detail', args=[document_id]))

    form = PartialImageForm(request.POST, request.FILES)
    if not form.is_valid():
        versionForm = PartialVersionForm()
        attachmentForm = PartialAttachmentForm()
        imageForm = form
        documentForm = PartialDocumentForm()
        documentForm.limitChoicesToValidStates(document)
        return render(request, 'documents/todo_detail.html', locals())

    content_files = request.FILES.getlist('content')
    files = []
    for content in content_files:
        try:
            image = Image.objects.get(document=document, content__endswith=content)
            image.content.save(content.name, content)
        except Image.DoesNotExist:
            image = Image(document=document, content=content)
            image.save()
        files.append({'name': os.path.basename(image.content.name), 'url': image.content.url})

    if 'application/json' in request.META['HTTP_ACCEPT']:
        from django.http import HttpResponse
        import json
        response_data = json.dumps({'files': files})
        return HttpResponse(response_data, content_type='application/json')

    return HttpResponseRedirect(reverse('todo_detail', args=[document_id]))

@login_required
@transaction.atomic
def add_version(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method != 'POST':
        return HttpResponseRedirect(reverse('todo_detail', args=[document_id]))

    form = PartialVersionForm(request.POST, request.FILES, 
                              contentMetaData=model_to_dict(document))
    if not form.is_valid():
        versionForm = form
        attachmentForm = PartialAttachmentForm()
        imageForm = PartialImageForm()
        documentForm = PartialDocumentForm()
        documentForm.limitChoicesToValidStates(document)
        return render(request, 'documents/todo_detail.html', locals())

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
        return render(request, 'documents/todo_detail.html', locals())

    document.transitionTo(form.cleaned_data['state'])
    return HttpResponseRedirect(reverse('todo_index'))

@login_required
@transaction.atomic
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

    return render(request, 'documents/todo_markup.html', locals())

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

    return render(request, 'documents/todo_sbsform.html', locals())

@login_required
def preview_sbsform_new(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method == 'POST':
        form = SBSFormForm(request.POST)
        if form.is_valid():
            inputFile = document.latest_version().content.path
            outputFile = Pipeline2.dtbook2sbsform(
                inputFile,
                document_identifier=document.identifier,
                use_local_dictionary=document.has_local_words(),
                **form.cleaned_data)

            if isinstance(outputFile, tuple):
                # if filename is a tuple we're actually looking at a list of error messages
                errorMessages = outputFile
                return render(request, 'documents/todo_sbsform.html', locals())

            contraction = form.cleaned_data['contraction']
            contraction_to_mimetype_mapping = {0 : 'text/x-sbsform-g0',
                                               1 : 'text/x-sbsform-g1',
                                               2 : 'text/x-sbsform-g2'}
            mimetype = contraction_to_mimetype_mapping.get(contraction, 'text/x-sbsform-g2')
            return render_to_mimetype_response(mimetype, document.title.encode('utf-8'), outputFile)
    else:
        form = SBSFormForm()

    return render(request, 'documents/todo_sbsform.html', locals())

@login_required
def preview_pdf(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method == 'POST':
        form = LargePrintProfileForm(request.POST)
        if form.is_valid():
            inputFile = document.latest_version().content.path
            outputFile = "/tmp/%s.pdf" % document_id
            StandardLargePrint.dtbook2pdf(inputFile, outputFile,
                                          images=document.image_set.all(), **form.cleaned_data)
            filename = document.title + u" " + form.cleaned_data['font_size']
            return render_to_mimetype_response('application/pdf', 
                                               filename.encode('utf-8'), outputFile)
    else:
        form = LargePrintProfileForm()

    return render(request, 'documents/todo_pdf.html', locals())

@login_required
def preview_library_pdf(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    inputFile = document.latest_version().content.path
    outputFile = "/tmp/%s.pdf" % document_id
    StandardLargePrint.dtbook2pdf(inputFile, outputFile, images=document.image_set.all())
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
            StandardLargePrint.dtbook2pdf(inputFile, outputFile,
                                          images=document.image_set.all(), **form.cleaned_data)
            filename = document.title + u" " + form.cleaned_data['font_size']
            return render_to_mimetype_response('application/pdf', 
                                               filename.encode('utf-8'), outputFile)
    else:
        form = SalePDFForm()

    return render(request, 'documents/todo_sale_pdf.html', locals())

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

    return render(request, 'documents/todo_rtf.html', locals())

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
            DaisyPipeline.dtbook2epub(inputFile, outputFile,
                                      images=document.image_set.all(), **defaults)
            return render_to_mimetype_response('application/epub+zip', 
                                               document.title.encode('utf-8'), outputFile)
    else:
        form = EPUBForm()

    return render(request, 'documents/todo_epub.html', locals())

@login_required
def preview_epub3(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method == 'POST':
        form = EPUB3Form(request.POST)
        if form.is_valid():
            inputFile = document.latest_version().content.path
            outputDir = tempfile.mkdtemp(prefix="daisyproducer-")
            
            ebookNumber = form.cleaned_data.pop('ebookNumber')

            filename = Pipeline2.dtbook2epub3(
                inputFile, outputDir,
                images=document.image_set.all(), **form.cleaned_data)
            if isinstance(filename, tuple):
                # if filename is a tuple we're actually looking at a list of error messages
                errorMessages = filename
                return render(request, 'documents/todo_epub3.html', locals())

            # put a copy of the ebook to a shared folder where it is fetched by another process that
            # puts into the distribution system. See fhs for a rationale about the dest folder
            # (http://www.pathname.com/fhs/pub/fhs-2.3.html#VARSPOOLAPPLICATIONSPOOLDATA)
            shutil.copy2(filename, os.path.join('/var/spool/daisyproducer', ebookNumber + '.epub'))

            return render_to_mimetype_response('application/epub+zip',
                                               document.title.encode('utf-8'), filename)
    else:
        ebook = Product.objects.filter(document=document, type=2)
        if ebook:
            form = EPUB3Form({'ebookNumber': ebook[0].identifier})
        else:
            form = EPUB3Form()

    return render(request, 'documents/todo_epub3.html', locals())

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
            zipFile.close() # we are only interested in a unique filename
            zipDirectory(outputDir, zipFile.name, document.title)
            shutil.rmtree(outputDir)

            return render_to_mimetype_response('application/zip', 
                                               document.title.encode('utf-8'), zipFile.name)
    else:
        form = DTBForm()

    return render(request, 'documents/todo_dtb.html', locals())

@login_required
def preview_odt(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method == 'POST':
        form = ODTForm(request.POST)
        if form.is_valid():
            inputFile = document.latest_version().content.path
            filename = Pipeline2.dtbook2odt(inputFile,
                                            imageFiles=document.image_set.all(),
                                            **form.cleaned_data)

            if isinstance(filename, tuple):
                # if filename is a tuple we're actually looking at a list of error messages
                errorMessages = filename
                return render(request, 'documents/todo_odt.html', locals())

            return render_to_mimetype_response('application/vnd.oasis.opendocument.text', 
                                               document.title.encode('utf-8'), filename)
    else:
        form = ODTForm()

    return render(request, 'documents/todo_odt.html', locals())

