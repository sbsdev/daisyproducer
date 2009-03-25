from django.shortcuts import render_to_response, get_object_or_404
from daisyproducer.documents.models import Document, BrailleProfileForm, LargePrintProfileForm
from django.http import HttpResponse, HttpResponseRedirect
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

    if not form.is_valid():
        return HttpResponseRedirect('/documents/%s' % document_id)

    document = Document.objects.get(pk=document_id)

    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = "attachment; filename=\"%s.pdf\"" % (document.title.encode('utf-8'))

    formData = form.cleaned_data
    
    fmtString = "--fontsize=%s --font=\"%s\" --pageStyle=%s --alignment=%s --papersize=%s"
    options = fmtString % (
        formData['fontSize'], 
        formData['font'], 
        formData['pageStyle'], 
        formData['alignment'],  
        formData['paperSize'])
    
    inputFile = document.content.path
    outputFile = "/tmp/%s.pdf" % document_id
    command = "dtbook2pdf %s %s %s >/dev/null" % (inputFile, outputFile, options)
    system(command)

    f = open(outputFile)
    try:
        pdf = f.read()
        response.write(pdf)
    finally:
        f.close()

    return response

def as_brl(request, document_id):
    form = BrailleProfileForm(request.POST)

    if not form.is_valid():
        return HttpResponseRedirect('/documents/%s' % document_id)

    document = Document.objects.get(pk=document_id)

    response = HttpResponse(mimetype='text/plain')
    response['Content-Disposition'] = "attachment; filename=\"%s.brl\"" % (document.title.encode('utf-8'))

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
    
    inputFile = document.content.path
    outputFile = "/tmp/%s.brl" % document_id
    command = "dtbook2brl %s %s %s >/dev/null" % (inputFile, outputFile, options)
    system(command)

    f = open(outputFile)
    try:
        pdf = f.read()
        response.write(pdf)
    finally:
        f.close()

    return response

