from daisyproducer.documents.external import DaisyPipeline
from daisyproducer.documents.models import Document, BrailleProfileForm, LargePrintProfileForm
from daisyproducer.utils import fields_for_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list, object_detail

from os import system

# browse use case
def index(request):
    """Show all the documents that approved and order them by title"""
    response = object_list(
        request,
        queryset = Document.objects.filter(state__name='approved').order_by('title'),
        template_name = 'documents/browse_index.html',
        extra_context = {'fields' : fields_for_model(Document())}
    )
    return response

def detail(request, document_id):
    lpform = LargePrintProfileForm()
    bform = BrailleProfileForm()
    fields = fields_for_model(Document())
    response = object_detail(
        request,
        queryset = Document.objects.all(),
        object_id = document_id,
        template_name = 'documents/browse_detail.html',
        extra_context = locals(),
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

    formData = form.cleaned_data

    contractionMap = {
        0 : 'de-de-g0.sbs.utb', 
        1 : 'de-de-g1.sbs.ctb', 
        2 : 'de-de-g2.sbs.ctb'}
    yesNoMap = {
        True : "yes", 
        False : "no" }

    fmtString = "-CcellsPerLine=\"%s\" -ClinesPerPage=\"%s\" -CliteraryTextTable=\"%s\" -Chyphenate=\"%s\" -CprintPages=\"%s\""
    options = fmtString % (
        formData['cellsPerLine'], 
        formData['linesPerPage'], 
        contractionMap[formData['contraction']], 
        yesNoMap[formData['hyphenation']], 
        yesNoMap[formData['showOriginalPageNumbers']])
    
    inputFile = document.latest_version().content.path
    outputFile = "/tmp/%s.brl" % document_id
    command = "dtbook2brl %s %s %s >/dev/null" % (inputFile, outputFile, options)
    system(command)

    return render_to_mimetype_response('text/plain', document.title.encode('utf-8'), outputFile)


def render_to_mimetype_response(mimetype, filename, outputFile):
    response = HttpResponse(mimetype=mimetype)
    response['Content-Disposition'] = "attachment; filename=\"%s\"" % (filename)

    f = open(outputFile)
    try:
        content = f.read()
        response.write(content)
    finally:
        f.close()

    return response

