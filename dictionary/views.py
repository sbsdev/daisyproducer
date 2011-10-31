import unicodedata

import louis
from django.core.urlresolvers import reverse
from django.db import transaction
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from lxml import etree

from dictionary.forms import BaseWordFormSet
from dictionary.models import Word
from documents.models import Document

@transaction.commit_on_success
def check(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method == 'POST':
        WordFormSet = modelformset_factory(
            Word, exclude=('documents', 'isConfirmed'), formset=BaseWordFormSet, can_delete=True)

        formset = WordFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.isConfirmed = False
                instance.save()
                instance.documents.add(document)
            return HttpResponseRedirect(reverse('todo_detail', args=[document_id]))
        else:
            return render_to_response('dictionary/words.html', locals(),
                                      context_instance=RequestContext(request))

    document.latest_version().content.open()
    tree = etree.parse(document.latest_version().content.file)
    document.latest_version().content.close()
    content = etree.tostring(tree, method="text", encoding=unicode)
    content = ''.join(c for c in content 
                      if unicodedata.category(c) in ['Lu', 'Ll', 'Zs', 'Zl', 'Zp'] 
                      or c in ['\n', '\r'])
    new_words = dict((w.lower(),1) for w in content.split() if len(w) > 1).keys()
    duplicate_words = [word.untranslated for 
                       word in Word.objects.filter(untranslated__in=new_words)]
    unknown_words = [{'untranslated': word, 
                      'grade1': louis.translateString(['de-ch-g1.ctb'], word),
                      'grade2': louis.translateString(['de-ch-g2.ctb'], word)} 
                     for word in new_words if word not in duplicate_words]
    unknown_words.sort(cmp=lambda x,y: cmp(x['untranslated'].lower(), y['untranslated'].lower()))

    WordFormSet = modelformset_factory(
        Word, exclude=('documents', 'isConfirmed'), 
        extra=len(unknown_words), formset=BaseWordFormSet, can_delete=True)

    formset = WordFormSet(queryset=Word.objects.none(), initial=unknown_words)

    return render_to_response('dictionary/words.html', locals(), 
                              context_instance=RequestContext(request))

def local(request, document_id):

    if request.method == 'POST':
        WordFormSet = modelformset_factory(
            Word, exclude=('documents', 'isConfirmed'), formset=BaseWordFormSet, can_delete=True)

        formset = WordFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(reverse('todo_detail', args=[document_id]))
        else:
            return render_to_response('dictionary/local.html', locals(),
                                      context_instance=RequestContext(request))

    document = get_object_or_404(Document, pk=document_id)
    WordFormSet = modelformset_factory(
        Word, exclude=('documents', 'isConfirmed'), formset=BaseWordFormSet, can_delete=True)

    formset = WordFormSet(queryset=Word.objects.filter(documents=document))

    return render_to_response('dictionary/local.html', locals(), 
                              context_instance=RequestContext(request))


@transaction.commit_on_success
def confirm(request):
    if request.method == 'POST':
        WordFormSet = modelformset_factory(Word, exclude=('documents'), formset=BaseWordFormSet)

        formset = WordFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save()
            for instance in instances:
                # TODO: don't clear the documents if the word is local
                instance.documents.clear()
            return HttpResponseRedirect(reverse('todo_index'))
        else:
            return render_to_response('dictionary/confirm.html', locals(),
                                      context_instance=RequestContext(request))

    WordFormSet = modelformset_factory(
        Word, exclude=('documents'), formset=BaseWordFormSet, extra=0)

    formset = WordFormSet(queryset=Word.objects.filter(isConfirmed=False))

    return render_to_response('dictionary/confirm.html', locals(), 
                              context_instance=RequestContext(request))


