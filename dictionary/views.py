import unicodedata

import louis
from dictionary.forms import BaseWordFormSet
from dictionary.models import Word
from django.core.urlresolvers import reverse
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from documents.models import Document
from lxml import etree


def dictionary(request, document_id):

    if request.method == 'POST':
        WordFormSet = modelformset_factory(
            Word, exclude=('document', 'isConfirmed'), formset=BaseWordFormSet, can_delete=True)

        formset = WordFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(reverse('todo_detail', args=[document_id]))
        else:
            return render_to_response('dictionary/words.html', locals(),
                                      context_instance=RequestContext(request))

    document = get_object_or_404(Document, pk=document_id)
    document.latest_version().content.open()
    tree = etree.parse(document.latest_version().content.file)
    document.latest_version().content.close()
    content = etree.tostring(tree, method="text", encoding=unicode)
    content = ''.join(c for c in content if unicodedata.category(c) in ['Lu', 'Ll', 'Zs', 'Zl'])
    new_words = dict((w.lower(),1) for w in content.split() if len(w) > 1).keys()
    duplicate_words = [word.untranslated for 
                       word in Word.objects.filter(untranslated__in=new_words)]
    unknown_words = [{'untranslated': word, 
                      'grade1': louis.translateString(['de-ch-g1.ctb'], word),
                      'grade2': louis.translateString(['de-ch-g2.ctb'], word)} 
                     for word in new_words if word not in duplicate_words]
    unknown_words.sort(cmp=lambda x,y: cmp(x['untranslated'].lower(), y['untranslated'].lower()))

    WordFormSet = modelformset_factory(
        Word, exclude=('document', 'isConfirmed'), 
        extra=len(unknown_words), formset=BaseWordFormSet, can_delete=True)

    formset = WordFormSet(queryset=Word.objects.none(), initial=unknown_words)

    return render_to_response('dictionary/words.html', locals(), 
                              context_instance=RequestContext(request))


def confirm(request):

    if request.method == 'POST':
        WordFormSet = modelformset_factory(
            Word, exclude=('document', 'isConfirmed'), formset=BaseWordFormSet, can_delete=True)

        formset = WordFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(reverse('todo_index'))
        else:
            return render_to_response('dictionary/confirm.html', locals(),
                                      context_instance=RequestContext(request))

    WordFormSet = modelformset_factory(
        Word, exclude=('document', 'isConfirmed'), formset=BaseWordFormSet, can_delete=True)

    formset = WordFormSet(queryset=Word.objects.filter(isConfirmed=False))

    return render_to_response('dictionary/confirm.html', locals(), 
                              context_instance=RequestContext(request))


