import os
import unicodedata

import louis
from daisyproducer.dictionary.brailleTables import writeLocalTables, getTables
from daisyproducer.dictionary.forms import RestrictedWordForm, RestrictedConfirmWordForm, BaseWordFormSet
from daisyproducer.dictionary.models import Word
from daisyproducer.documents.models import Document
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import transaction
from django.forms.models import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.encoding import smart_unicode
from lxml import etree

BRL_NAMESPACE = {'brl':'http://www.daisy.org/z3986/2009/braille/'}

@transaction.commit_on_success
def check(request, document_id, grade):

    document = get_object_or_404(Document, pk=document_id)

    if request.method == 'POST':
        WordFormSet = modelformset_factory(
            Word, 
            form=RestrictedWordForm,
            exclude=('document', 'isConfirmed', 'grade'), 
            can_delete=True)

        formset = WordFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.grade = grade
                instance.document = document
                instance.save()
            writeLocalTables([document])
            return HttpResponseRedirect(reverse('todo_detail', args=[document_id]))
        else:
            return render_to_response('dictionary/words.html', locals(),
                                      context_instance=RequestContext(request))

    document.latest_version().content.open()
    tree = etree.parse(document.latest_version().content.file)
    document.latest_version().content.close()
    # grab the homographs
    homographs = set(("|".join(homograph.xpath('text()')).lower() 
                      for homograph in tree.xpath('//brl:homograph', namespaces=BRL_NAMESPACE)))
    duplicate_homographs = set((smart_unicode(word.homograph_disambiguation) for 
                                word in Word.objects.filter(grade=grade).filter(type=5).filter(homograph_disambiguation__in=homographs)))
    unknown_homographs = [{'untranslated': homograph.replace('|', ''), 
                           'braille': louis.translateString(getTables(grade), homograph.replace('|', unichr(0x250A))),
                           'type': 5,
                           'homograph_disambiguation': homograph} 
                          for homograph in homographs - duplicate_homographs]
    # grab names and places
    names = set((name.text.lower() for name in tree.xpath('//brl:name', namespaces=BRL_NAMESPACE)))
    duplicate_names = set((smart_unicode(word.untranslated) for 
                           word in Word.objects.filter(grade=grade).filter(type__in=(1,2)).filter(untranslated__in=names)))
    unknown_names = [{'untranslated': name, 
                      'braille': louis.translateString(getTables(grade, name=True), name), 
                      'type': 2} 
                     for name in names - duplicate_names]
    places = set((place.text.lower() for place in tree.xpath('//brl:place', namespaces=BRL_NAMESPACE)))
    duplicate_places = set((smart_unicode(word.untranslated) for 
                            word in Word.objects.filter(grade=grade).filter(type__in=(3,4)).filter(untranslated__in=places)))
    unknown_places = [{'untranslated': place,
                       'braille': louis.translateString(getTables(grade, place=True), place),
                       'type': 4} 
                      for place in places - duplicate_places]
    # filter homographs, names and places from the xml
    xsl = etree.parse(os.path.join(settings.PROJECT_DIR, 'dictionary', 'xslt', 'filter.xsl'))
    transform = etree.XSLT(xsl)
    filtered_tree = transform(tree)
    # grab the rest of the content
    content = etree.tostring(filtered_tree, method="text", encoding=unicode)
    # filter all punctuation and replace dashes by space, so we can split by space below
    content = ''.join(
        # replace Punctuation Dash and Punctuation other with space
        c if unicodedata.category(c) not in ['Pd', 'Po'] else ' '
        for c in content 
        # drop all chars which are not letters, separators or select
        # punctuation which we replace with space later on
        if unicodedata.category(c) in ['Lu', 'Ll', 'Zs', 'Zl', 'Zp', 'Pd', 'Po']
        or c in ['\n', '\r'])
    new_words = set((w.lower() for w in content.split() if len(w) > 1))
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
    duplicate_words = set((smart_unicode(word.untranslated) for 
                           word in Word.objects.filter(grade=grade).filter(untranslated__in=new_words)))
    unknown_words = [{'untranslated': word, 
                      'braille': louis.translateString(getTables(grade), word),
                      'type' : 0} 
                     for word in new_words - duplicate_words]

    unknown_words = unknown_words + unknown_homographs + unknown_names + unknown_places
    unknown_words.sort(cmp=lambda x,y: cmp(x['untranslated'].lower(), y['untranslated'].lower()))

    WordFormSet = modelformset_factory(
        Word, 
        form=RestrictedWordForm,
        exclude=('document', 'isConfirmed', 'grade'), 
        extra=len(unknown_words), can_delete=True)

    formset = WordFormSet(queryset=Word.objects.none(), initial=unknown_words)

    stats = { "total_words": len(new_words), 
              "total_new": len(unknown_words), 
              "percent": 100.0*len(unknown_words)/len(new_words) }

    return render_to_response('dictionary/words.html', locals(),
                              context_instance=RequestContext(request))

@transaction.commit_on_success
def local(request, document_id, grade):

    document = get_object_or_404(Document, pk=document_id)
    if request.method == 'POST':
        WordFormSet = modelformset_factory(
            Word, 
            form=RestrictedWordForm,
            exclude=('document', 'isConfirmed', 'grade'), 
            can_delete=True)

        formset = WordFormSet(request.POST, 
                              queryset=Word.objects.filter(document=document))
        if formset.is_valid():
            instances = formset.save()
            writeLocalTables([document])
            return HttpResponseRedirect(reverse('todo_detail', args=[document_id]))
        else:
            return render_to_response('dictionary/local.html', locals(),
                                      context_instance=RequestContext(request))

    WordFormSet = modelformset_factory(
        Word, 
        form=RestrictedWordForm,
        exclude=('document', 'isConfirmed', 'grade'), 
        can_delete=True, extra=0)

    formset = WordFormSet(queryset=Word.objects.filter(grade=grade).filter(document=document).order_by('untranslated', 'type'))

    return render_to_response('dictionary/local.html', locals(), 
                              context_instance=RequestContext(request))

@transaction.commit_on_success
def confirm(request, grade):
    if request.method == 'POST':
        WordFormSet = modelformset_factory(
            Word, 
            form=RestrictedConfirmWordForm,
            formset=BaseWordFormSet,
            exclude=('document', 'grade'),
            can_delete=True)

        formset = WordFormSet(request.POST, 
                              queryset=Word.objects.filter(isConfirmed=False))
        if formset.is_valid():
            instances = formset.save(commit=False)
            changedDocuments = set()
            for instance in instances:
                if instance.isConfirmed and not instance.isLocal:
                    # clear the documents if the word is not local
                    changedDocuments.add(instance.document)
                    instance.document = None
                    instance.save()
    # FIXME: in principle we need to regenerate the liblouis tables,
    # i.e. the white lists now. However we do this asynchronously
    # (using a cron job) for now. There are several reasons for this:
    # 1) It is slow as hell if done inside a transaction. To do this
    # outside the transaction we need transaction context managers
    # (https://docs.djangoproject.com/en/1.3/topics/db/transactions/#controlling-transaction-management-in-views)
    # which are only available in Django 1.3.
    # 2) We need to serialize the table writing so they do not write
    # on top of each other. This is easy if it is done periodically.
    # 3) Of course it would be nice to use some kind of message queue
    # for this (e.g. rabbitmq and celery), but for now this poor mans
    # solution seems good enough
            return HttpResponseRedirect(reverse('todo_index'))
        else:
            return render_to_response('dictionary/confirm.html', locals(),
                                      context_instance=RequestContext(request))

    # create a default for all unconfirmed homographs which have no default, i.e. no restriction word entry
    unconfirmed_homographs = set(Word.objects.filter(grade=grade).filter(type=5).filter(isConfirmed=False).values_list('untranslated', flat=True))
    covered_entries = set(Word.objects.filter(grade=grade).filter(type=0).filter(untranslated__in=unconfirmed_homographs).values_list('untranslated', flat=True))

    for word in unconfirmed_homographs - covered_entries:
        w = Word(untranslated=word, 
                 braille=louis.translateString(getTables(grade), word),
                 grade=grade, type=0)
        w.save()
    
    WordFormSet = modelformset_factory(
        Word, 
        form=RestrictedConfirmWordForm,
        formset=BaseWordFormSet,
        exclude=('document', 'grade'), extra=0,
        can_delete=True)

    formset = WordFormSet(queryset=Word.objects.filter(grade=grade).filter(isConfirmed=False).order_by('untranslated', 'type'))
    return render_to_response('dictionary/confirm.html', locals(), 
                              context_instance=RequestContext(request))


