import os
import unicodedata

import louis
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import transaction
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from lxml import etree

from dictionary.brailleTables import writeWhiteListTables, writeLocalTables
from dictionary.models import Word
from documents.models import Document


@transaction.commit_on_success
def check(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if request.method == 'POST':
        WordFormSet = modelformset_factory(Word, exclude=('documents', 'isConfirmed'), can_delete=True)

        formset = WordFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save()
            for instance in instances:
                instance.documents.add(document)
            writeLocalTables([document])
            return HttpResponseRedirect(reverse('todo_detail', args=[document_id]))
        else:
            return render_to_response('dictionary/words.html', locals(),
                                      context_instance=RequestContext(request))

    document.latest_version().content.open()
    tree = etree.parse(document.latest_version().content.file)
    document.latest_version().content.close()
    xsl = etree.parse(os.path.join(settings.PROJECT_DIR, 'dictionary', 'xslt', 'filter.xsl'))
    transform = etree.XSLT(xsl)
    filtered_tree = transform(tree)
    content = etree.tostring(filtered_tree, method="text", encoding=unicode)
    content = ''.join(c for c in content 
                      if unicodedata.category(c) in ['Lu', 'Ll', 'Zs', 'Zl', 'Zp'] 
                      or c in ['\n', '\r'])
    new_words = dict((w.lower(),1) for w in content.split() if len(w) > 1).keys()
    # FIXME: We basically do a set difference manually here. This
    # would probably be better if done inside the db. However for that
    # we would have to be able to insert the new_words into the db in
    # an efficient manner, i.e. bulk insert. For a possibility on how
    # to do this in the context of Django ORM look at
    # http://ole-laursen.blogspot.com/2010/11/bulk-inserting-django-objects.html.
    # After that we could for example do a query along the lines of
    # cursor.execute("SELECT untranslated from new_words EXCEPT SELECT
    # untranslated FROM dict_words;). However MySQL doesn't seem to
    # support EXCEPT so it would be SELECT untranslated FROM new_words
    # w1 LEFT JOIN dict_words w2 ON w1.untranslated=w2.untranslated
    # WHERE w2.untranslated IS NULL;
    duplicate_words = [word.untranslated for 
                       word in Word.objects.filter(untranslated__in=new_words)]
    unknown_words = [{'untranslated': word, 
                      'grade1': louis.translateString(['de-ch-g1.ctb'], word),
                      'grade2': louis.translateString(['de-ch-g2.ctb'], word)} 
                     for word in new_words if word not in duplicate_words]
    unknown_words.sort(cmp=lambda x,y: cmp(x['untranslated'].lower(), y['untranslated'].lower()))

    WordFormSet = modelformset_factory(
        Word, exclude=('documents', 'isConfirmed'), 
        extra=len(unknown_words), can_delete=True)

    formset = WordFormSet(queryset=Word.objects.none(), initial=unknown_words)

    stats = { "total_words": len(new_words), 
              "total_new": len(unknown_words), 
              "percent": 100.0*len(unknown_words)/len(new_words) }

    return render_to_response('dictionary/words.html', locals(),
                              context_instance=RequestContext(request))

def local(request, document_id):

    document = get_object_or_404(Document, pk=document_id)
    if request.method == 'POST':
        WordFormSet = modelformset_factory(Word, exclude=('documents', 'isConfirmed'), can_delete=True)

        formset = WordFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            writeLocalTables([document])
            return HttpResponseRedirect(reverse('todo_detail', args=[document_id]))
        else:
            return render_to_response('dictionary/local.html', locals(),
                                      context_instance=RequestContext(request))

    WordFormSet = modelformset_factory(
        Word, exclude=('documents', 'isConfirmed'), can_delete=True, extra=0)

    formset = WordFormSet(queryset=Word.objects.filter(documents=document))

    return render_to_response('dictionary/local.html', locals(), 
                              context_instance=RequestContext(request))


@transaction.commit_on_success
def confirm(request):
    if request.method == 'POST':
        WordFormSet = modelformset_factory(Word, exclude=('documents'))

        formset = WordFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save()
            changedDocuments = set()
            for instance in instances:
                if instance.isConfirmed and not instance.isLocal:
                    # clear the documents if the word is not local
                    changedDocuments.update(instance.documents.all())
                    instance.documents.clear()
            # write new global white lists
            writeWhiteListTables(Word.objects.filter(isConfirmed=True).filter(isLocal=False).order_by('untranslated'))
            # update local tables
            writeLocalTables(changedDocuments)
            return HttpResponseRedirect(reverse('todo_index'))
        else:
            return render_to_response('dictionary/confirm.html', locals(),
                                      context_instance=RequestContext(request))

    WordFormSet = modelformset_factory(Word, exclude=('documents'), extra=0)

    formset = WordFormSet(queryset=Word.objects.filter(isConfirmed=False))
    return render_to_response('dictionary/confirm.html', locals(), 
                              context_instance=RequestContext(request))


