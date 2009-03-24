from django.shortcuts import render_to_response, get_object_or_404
from daisyproducer.documents.models import Document
from django.http import HttpResponse
from django import forms

from os import system

FONTSIZE_CHOICES = (
    ('12pt', '12pt'),
    ('14pt', '14pt'),
    ('17pt', '17pt'),
    ('20pt', '20pt'),
)

FONT_CHOICES = (
    ('Tiresias LPfont', 'Tiresias LPfont'),
    ('LMRoman10 Regular', 'LMRoman10 Regular'),
    ('LMSans10 Regular', 'LMSans10 Regular'),
    ('LMTypewriter10 Regular', 'LMTypewriter10 Regular'),
)

PAGESTYLE_CHOICES = (
    ('plain', 'Plain'),
    ('withPageNums', 'With original page numbers'),
    ('scientific', 'Scientific'),
)

ALIGNMENT_CHOICES = (
    ('justified', 'justified'),
    ('left', 'left aligned'),
)

PAPERSIZE_CHOICES = (
    ('a3paper', 'a3paper'),
    ('a4paper', 'a4paper'),
)

class LargePrintDownloadForm(forms.Form):
    fontSize = forms.ChoiceField(choices=FONTSIZE_CHOICES)
    font = forms.ChoiceField(choices=FONT_CHOICES)
    pageStyle = forms.ChoiceField(choices=PAGESTYLE_CHOICES)
    alignment = forms.ChoiceField(choices=ALIGNMENT_CHOICES)
    paperSize = forms.ChoiceField(choices=PAPERSIZE_CHOICES)

def index(request):
    document_list = Document.objects.all()
    return render_to_response('documents/index.html', {'document_list': document_list})

def detail(request, document_id):
    d = get_object_or_404(Document, pk=document_id)
    lpform = LargePrintDownloadForm()
    return render_to_response('documents/detail.html', {'document': d, 'lpform' : lpform})

def as_pdf(request, document_id):
    form = LargePrintDownloadForm(request.POST)

    document = Document.objects.get(id=document_id)

    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = "attachment; filename=%s.pdf" % (document.title)

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

