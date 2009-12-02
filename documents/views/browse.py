from daisyproducer.documents.external import DaisyPipeline, Liblouis, SBSForms
from daisyproducer.documents.forms import SBSFormsForm
from daisyproducer.documents.models import Document, BrailleProfileForm, LargePrintProfileForm
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
            'sform' : SBSFormsForm()}
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

    return render_to_mimetype_response('text/plain', document.title.encode('utf-8'), outputFile)

def as_sbsforms(request, document_id):
    form = SBSFormsForm(request.POST)

    if not form.is_valid():
        return HttpResponseRedirect(reverse('browse_detail', args=[document_id]))

    document = Document.objects.get(pk=document_id)
    inputFile = document.latest_version().content.path
    outputFile = "/tmp/%s.sbsforms" % document_id
    SBSForms.dtbook2sbsforms(inputFile, outputFile, **form.cleaned_data)

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

