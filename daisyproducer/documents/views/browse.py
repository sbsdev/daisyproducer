import os.path
import shutil
import tempfile

from daisyproducer.documents.external import DaisyPipeline, Liblouis, SBSForm, zipDirectory
from daisyproducer.documents.forms import SBSFormForm, TextOnlyDTBForm
from daisyproducer.documents.models import State, Document, BrailleProfileForm, LargePrintProfileForm
from daisyproducer.documents.views.utils import render_to_mimetype_response
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView
from django.db.models import Max

class BrowseListView(ListView):
    template_name = 'documents/browse_index.html'

    def get_queryset(self):
        final_sort_order = State.objects.aggregate(final_sort_order=Max('sort_order')).get('final_sort_order')
        return Document.objects.filter(state__sort_order=final_sort_order).order_by('title')

    def dispatch(self, request, *args, **kwargs):
        # we only show this view to anonymous users
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('todo_index'))
        return super(BrowseListView, self).dispatch(request, *args, **kwargs)

class BrowseDetailView(DetailView):
    template_name = 'documents/browse_detail.html'
    queryset = Document.objects.all()

    def get_context_data(self, **kwargs):
        context = super(BrowseDetailView, self).get_context_data(**kwargs)
        context.update({
            'lpform' : LargePrintProfileForm(),
            'bform' : BrailleProfileForm(),
            'sform' : SBSFormForm(),
            'textonlydtbform' : TextOnlyDTBForm()})
        return context

def as_pdf(request, document_id):
    form = LargePrintProfileForm(request.POST)

    if not form.is_valid():
        return HttpResponseRedirect(reverse('browse_detail', args=[document_id]))

    document = Document.objects.get(pk=document_id)

    inputFile = document.latest_version().content.path
    outputFile = "/tmp/%s.pdf" % document_id
    DaisyPipeline.dtbook2pdf(inputFile, outputFile,
                             images=document.image_set.all(), **form.cleaned_data)

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
    contraction = form.cleaned_data['contraction']
    contraction_to_mimetype_mapping = {0 : 'text/x-sbsform-g0', 
                                       1 : 'text/x-sbsform-g1',
                                       2 : 'text/x-sbsform-g2'}
    mimetype = contraction_to_mimetype_mapping.get(contraction, 'text/x-sbsform-g2')
    return render_to_mimetype_response(mimetype, document.title.encode('utf-8'), outputFile)

def as_text_only_dtb(request, document_id):
    form = TextOnlyDTBForm(request.POST)

    if not form.is_valid():
        return HttpResponseRedirect(reverse('browse_detail', args=[document_id]))

    document = Document.objects.get(pk=document_id)
    inputFile = document.latest_version().content.path
    outputDir = tempfile.mkdtemp(prefix="daisyproducer-")

    DaisyPipeline.dtbook2text_only_dtb(
        inputFile, outputDir,
        images=document.image_set.all(), **form.cleaned_data)

    zipFile = tempfile.NamedTemporaryFile(suffix='.zip', prefix=document_id, delete=False)
    zipFile.close() # we are only interested in a unique filename
    zipDirectory(outputDir, zipFile.name, document.title)
    shutil.rmtree(outputDir)
    
    return render_to_mimetype_response('application/zip', document.title.encode('utf-8'), zipFile.name)
