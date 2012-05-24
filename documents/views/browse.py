import os.path
import shutil
import tempfile

from daisyproducer.documents.external import DaisyPipeline, Liblouis, SBSForm, zipDirectory
from daisyproducer.documents.forms import SBSFormForm, RTFForm, XHTMLForm, EPUBForm, TextOnlyDTBForm, DTBForm
from daisyproducer.documents.models import State, Document, BrailleProfileForm, LargePrintProfileForm
from daisyproducer.documents.views.utils import render_to_mimetype_response
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic.list_detail import object_list, object_detail
from django.db.models import Max


# browse use case
def index(request):
    """Show all the documents that are in the final state and order them by title"""
    # we only show this view to anonymous users
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('todo_index'))

    final_sort_order = State.objects.aggregate(final_sort_order=Max('sort_order')).get('final_sort_order')
    response = object_list(
        request,
        queryset = Document.objects.filter(state__sort_order=final_sort_order).order_by('title'),
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
            'textonlydtbform' : TextOnlyDTBForm(),
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

def as_text_only_dtb(request, document_id):
    form = TextOnlyDTBForm(request.POST)

    if not form.is_valid():
        return HttpResponseRedirect(reverse('browse_detail', args=[document_id]))

    document = Document.objects.get(pk=document_id)
    inputFile = document.latest_version().content.path
    outputDir = tempfile.mkdtemp(prefix="daisyproducer-")

    DaisyPipeline.dtbook2text_only_dtb(inputFile, outputDir, **form.cleaned_data)

    zipFile = tempfile.NamedTemporaryFile(suffix='.zip', prefix=document_id, delete=False)
    zipDirectory(outputDir, zipFile.name, document.title)
    shutil.rmtree(outputDir)
    
    return render_to_mimetype_response('application/zip', document.title.encode('utf-8'), zipFile.name)

def as_dtb(request, document_id):
    form = DTBForm(request.POST)

    if not form.is_valid():
        return HttpResponseRedirect(reverse('browse_detail', args=[document_id]))

    document = Document.objects.get(pk=document_id)
    inputFile = document.latest_version().content.path
    outputDir = tempfile.mkdtemp(prefix="daisyproducer-")

    DaisyPipeline.dtbook2dtb(inputFile, outputDir, **form.cleaned_data)

    zipFile = tempfile.NamedTemporaryFile(suffix='.zip', prefix=document_id, delete=False)
    zipDirectory(outputDir, zipFile.name, document.title)
    shutil.rmtree(outputDir)

    return render_to_mimetype_response('application/zip', document.title.encode('utf-8'), zipFile.name)

