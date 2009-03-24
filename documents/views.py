from django.shortcuts import render_to_response, get_object_or_404
from daisyproducer.documents.models import Document, BrailleProfileForm, LargePrintProfileForm
from django.http import HttpResponse
from django import forms

from os import system

def index(request):
    document_list = Document.objects.all()
    return render_to_response('documents/index.html', {'document_list': document_list})

def detail(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    lpform = LargePrintProfileForm()
    bform = BrailleProfileForm()
    return render_to_response('documents/detail.html', locals())

def as_pdf(request, document_id):
    form = LargePrintProfileForm(request.POST)

    document = Document.objects.get(pk=document_id)

    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = "attachment; filename=\"%s.pdf\"" % (document.title)

    if not form.is_valid():
        return HttpResponseRedirect('/documents/')

    fontSize = form.cleaned_data['fontSize']
    font = form.cleaned_data['font']
    pageStyle = form.cleaned_data['pageStyle']
    alignment = form.cleaned_data['alignment']
    paperSize = form.cleaned_data['paperSize']
    
    options = "--fontsize=%s --font=\"%s\" --pageStyle=%s --alignment=%s --papersize=%s" % (fontSize, font, pageStyle, alignment, paperSize)
    
    inputFile = document.content.path
    outputFile = "/tmp/foo.pdf"
    command = "dtbook2pdf %s %s %s >/dev/null" % (inputFile, outputFile, options)
    system(command)

    f = open(outputFile)
    try:
        pdf = f.read()
        response.write(pdf)
    finally:
        f.close()

    return response

