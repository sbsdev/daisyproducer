import os.path
import shutil
import tempfile
import zipfile

from daisyproducer.documents.external import DaisyPipeline, Liblouis, SBSForm
from daisyproducer.documents.forms import SBSFormForm, RTFForm, XHTMLForm, EPUBForm, TextOnlyFilesetForm, DTBForm
from daisyproducer.documents.models import Document, BrailleProfileForm, LargePrintProfileForm
from daisyproducer.documents.views.utils import render_to_mimetype_response
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic.list_detail import object_list, object_detail


# browse use case
def index(request):
    """Show all the documents that approved and order them by title"""
    response = object_list(
        request,
        queryset = Document.objects.filter(state__name='approved').order_by('title'),
        template_name = 'documents/browse_index.html'
    )
    return response

def detail(request, document_id):
    response = object_detail(
        request,
        queryset = Document.objects.all(),
        object_id = document_id,
        template_name = 'documents/browse_detail.html',
        extra_context = {
            'lpform' : LargePrintProfileForm(),
            'bform' : BrailleProfileForm(),
            'sform' : SBSFormForm(),
            'xhtmlform' : XHTMLForm(),
            'rtfform' : RTFForm(),
            'textonlyfilesetform' : TextOnlyFilesetForm(),
            'dtbform' : DTBForm()}
        )
    return response

def as_pdf(request, document_id):
    form = LargePrintProfileForm(request.POST)

    if not form.is_valid():
        return HttpResponseRedirect(reverse('browse_detail', args=[document_id]))

    document = Document.objects.get(pk=document_id)

    inputFile = document.latest_version().content.path
    outputFile = "/tmp/%s.pdf" % document_id
    DaisyPipeline.dtbook2pdf(inputFile, outputFile, **form.cleaned_data)

    return render_to_mimetype_response('application/pdf', document.title.encode('utf-8'), outputFile)

def as_brl(request, document_id):
    form = BrailleProfileForm(request.POST)

    if not form.is_valid():
        return HttpResponseRedirect(reverse('browse_detail', args=[document_id]))

    document = Document.objects.get(pk=document_id)

    inputFile = document.latest_version().content.path
    outputFile = "/tmp/%s.brl" % document_id
    Liblouis.dtbook2brl(inputFile, outputFile, **form.cleaned_data)

    return render_to_mimetype_response('text/x-brl', document.title.encode('utf-8'), outputFile)

def as_sbsform(request, document_id):
    form = SBSFormForm(request.POST)

    if not form.is_valid():
        return HttpResponseRedirect(reverse('browse_detail', args=[document_id]))

    document = Document.objects.get(pk=document_id)
    inputFile = document.latest_version().content.path
    outputFile = "/tmp/%s.sbsform" % document_id
    SBSForm.dtbook2sbsform(inputFile, outputFile, **form.cleaned_data)

    return render_to_mimetype_response('text/x-sbsform', document.title.encode('utf-8'), outputFile)

def as_xhtml(request, document_id):
    form = XHTMLForm(request.POST)

    if not form.is_valid():
        return HttpResponseRedirect(reverse('browse_detail', args=[document_id]))

    document = Document.objects.get(pk=document_id)
    inputFile = document.latest_version().content.path
    outputFile = "/tmp/%s.xhtml" % document_id
    DaisyPipeline.dtbook2xhtml(inputFile, outputFile, **form.cleaned_data)

    return render_to_mimetype_response('text/html', document.title.encode('utf-8'), outputFile)

def as_rtf(request, document_id):
    form = RTFForm(request.POST)

    if not form.is_valid():
        return HttpResponseRedirect(reverse('browse_detail', args=[document_id]))

    document = Document.objects.get(pk=document_id)
    inputFile = document.latest_version().content.path
    outputFile = "/tmp/%s.rtf" % document_id
    DaisyPipeline.dtbook2rtf(inputFile, outputFile, **form.cleaned_data)

    return render_to_mimetype_response('application/rtf', document.title.encode('utf-8'), outputFile)

def as_epub(request, document_id):
    form = EPUBForm(request.POST)

    if not form.is_valid():
        return HttpResponseRedirect(reverse('browse_detail', args=[document_id]))

    document = Document.objects.get(pk=document_id)
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

    return render_to_mimetype_response('application/epub+zip', document.title.encode('utf-8'), outputFile)

def zipDirectory(directory, zipFileName, document_title):
    outputFile = zipfile.ZipFile(zipFileName, 'w')
    cwd = os.getcwd()
    os.chdir(directory)
    for dirpath, dirnames, filenames in os.walk('.'):
        for filename in filenames:
            # zipFile support in Python has a few weak spots: Older
            # Pythons die if the filename or the arcname that is
            # passed to ZipFile.write is not in the right encoding
            # FIXME: remove the encode("latin-1") workaround once we
            # upgrade to 2.6.2
            outputFile.write(
                os.path.join(dirpath, filename).encode("latin-1"), 
                os.path.join(document_title, dirpath, filename).encode("latin-1"))
    outputFile.close()
    os.chdir(cwd)

def as_text_only_fileset(request, document_id):
    form = TextOnlyFilesetForm(request.POST)

    if not form.is_valid():
        return HttpResponseRedirect(reverse('browse_detail', args=[document_id]))

    document = Document.objects.get(pk=document_id)
    inputFile = document.latest_version().content.path
    outputDir = tempfile.mkdtemp(prefix="daisyproducer-")

    DaisyPipeline.dtbook2text_only_fileset(inputFile, outputDir, **form.cleaned_data)

    ignore, zipFileName = tempfile.mkstemp(suffix='.zip', prefix=document_id)
    zipDirectory(outputDir, zipFileName, document.title)
    shutil.rmtree(outputDir)
    
    return render_to_mimetype_response('application/zip', document.title.encode('utf-8'), zipFileName)

def as_dtb(request, document_id):
    form = DTBForm(request.POST)

    if not form.is_valid():
        return HttpResponseRedirect(reverse('browse_detail', args=[document_id]))

    document = Document.objects.get(pk=document_id)
    inputFile = document.latest_version().content.path
    outputDir = tempfile.mkdtemp(prefix="daisyproducer-")

    DaisyPipeline.dtbook2dtb(inputFile, outputDir, **form.cleaned_data)

    ignore, zipFileName = tempfile.mkstemp(suffix='.zip', prefix=document_id)
    zipDirectory(outputDir, zipFileName, document.title)
    shutil.rmtree(outputDir)

    return render_to_mimetype_response('application/zip', document.title.encode('utf-8'), zipFileName)

