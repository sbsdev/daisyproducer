import os
import unicodedata

import louis
from daisyproducer.dictionary.brailleTables import writeWhiteListTables, writeLocalTables, writeWordSplitTable
from daisyproducer.dictionary.models import Word
from daisyproducer.documents.models import Document
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import transaction
from django import forms
from django.forms.models import modelformset_factory, ModelForm
from django.forms.widgets import TextInput
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.encoding import smart_unicode
from lxml import etree

WORDSPLIT_TABLES_GRADE1 = ['sbs-wordsplit.dis', 'sbs-de-core6.cti', 'sbs-de-accents.cti', 
                           'sbs-special.cti', 'sbs-whitespace.mod', 'sbs-de-letsign.mod', 
                           'sbs-numsign.mod', 'sbs-litdigit-upper.mod', 'sbs-de-core.mod', 
                           'sbs-de-g1-wordsplit.mod', 'sbs-de-g1-core.mod', 'sbs-special.mod']

WORDSPLIT_TABLES_GRADE2 = WORDSPLIT_TABLES_GRADE1[:]
WORDSPLIT_TABLES_GRADE2[9:11] = ('sbs-de-g2-wordsplit.mod', 'sbs-de-g2-core.mod')

NAME_WORDSPLIT_TABLES_GRADE2 = WORDSPLIT_TABLES_GRADE2[:]
NAME_WORDSPLIT_TABLES_GRADE2[9:11] = ('sbs-de-name-wordsplit.mod', 'sbs-de-g2-name.mod')

PLACE_WORDSPLIT_TABLES_GRADE2 = WORDSPLIT_TABLES_GRADE2[:]
PLACE_WORDSPLIT_TABLES_GRADE2[9:11] = ('sbs-de-place-wordsplit.mod', 'sbs-de-g2-place.mod', 'sbs-de-g2-name.mod')

BRL_NAMESPACE = {'brl':'http://www.daisy.org/z3986/2009/braille/'}

class PartialWordForm(ModelForm):
    class Meta:
        model = Word
        exclude=('documents', 'isConfirmed', 'created_at', 'modified_at', 'modified_by'), 
        widgets = {
            'untranslated': TextInput(attrs={'readonly': 'readonly'}),
            }

    # make sure grade1 and grade2 have the same number of hyphenation points
    def clean(self):
        cleaned_data = self.cleaned_data
        grade1 = cleaned_data.get("grade1")
        grade2 = cleaned_data.get("grade2")

        if grade1 and grade2 and len(grade1.split('w')) != len(grade2.split('w')):
            raise forms.ValidationError("Grade1 and Grade2 do not have the same number of hyphenation points")

        return cleaned_data

class RestrictedWordForm(PartialWordForm):
    def __init__(self, *args, **kwargs):
        super(RestrictedWordForm, self).__init__(*args, **kwargs)
        if not self.is_bound:
            if self.initial['type'] == 0:
                typeChoices = [(id, name) for (id, name) in Word.WORD_TYPE_CHOICES if id in (0, 2, 4)]
            else:
                typeChoices = [(id, name) for (id, name) in Word.WORD_TYPE_CHOICES if id == self.initial['type']]
            self.fields['type'].choices = typeChoices

    # only clean if a word is not ignored
    def clean(self):
        cleaned_data = self.cleaned_data
        delete = cleaned_data.get("DELETE")

        if not delete:
            return super(RestrictedWordForm, self).clean()

        return cleaned_data

class RestrictedConfirmWordForm(PartialWordForm):
    def __init__(self, *args, **kwargs):
        super(RestrictedConfirmWordForm, self).__init__(*args, **kwargs)
        if not self.is_bound:
            if self.initial['type'] == 0:
                typeChoices = [(id, name) for (id, name) in Word.WORD_TYPE_CHOICES if id in (0, 1, 2, 3, 4)]
            elif self.initial['type'] == 2:
                typeChoices = [(id, name) for (id, name) in Word.WORD_TYPE_CHOICES if id in (1, 2)]
                self.initial['use_for_word_splitting'] = False
            elif self.initial['type'] == 4:
                typeChoices = [(id, name) for (id, name) in Word.WORD_TYPE_CHOICES if id in (3, 4)]
                self.initial['use_for_word_splitting'] = False
            else:
                typeChoices = [(id, name) for (id, name) in Word.WORD_TYPE_CHOICES if id == self.initial['type']]
            self.fields['type'].choices = typeChoices

    # only clean if a word is confirmed
    def clean(self):
        cleaned_data = self.cleaned_data
        isConfirmed = cleaned_data.get("isConfirmed")

        if isConfirmed:
            return super(RestrictedConfirmWordForm, self).clean()

        return cleaned_data

def removeRedundantSplitpoints(contraction):
    return "w".join(filter(None,contraction.split('w')))

@transaction.commit_on_success
def check(request, document_id):

    document = get_object_or_404(Document, pk=document_id)

    if request.method == 'POST':
        WordFormSet = modelformset_factory(
            Word, 
            form=RestrictedWordForm,
            exclude=('documents', 'isConfirmed', 'use_for_word_splitting', 'created_at', 'modified_at', 'modified_by'), 
            can_delete=True)

        formset = WordFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.modified_by = request.user
                instance.save()
                instance.documents.add(document)
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
                                word in Word.objects.filter(type=5).filter(homograph_disambiguation__in=homographs)))
    unknown_homographs = [{'untranslated': homograph.replace('|', ''), 
                           'grade1': removeRedundantSplitpoints(louis.translateString(WORDSPLIT_TABLES_GRADE1, homograph.replace('|', unichr(0x250A)))),
                           'grade2': removeRedundantSplitpoints(louis.translateString(WORDSPLIT_TABLES_GRADE2, homograph.replace('|', unichr(0x250A)))),
                           'type': 5,
                           'homograph_disambiguation': homograph} 
                          for homograph in homographs - duplicate_homographs]
    # grab names and places
    names = set((name.text.lower() for name in tree.xpath('//brl:name', namespaces=BRL_NAMESPACE)))
    duplicate_names = set((smart_unicode(word.untranslated) for 
                           word in Word.objects.filter(type__in=(1,2)).filter(untranslated__in=names)))
    unknown_names = [{'untranslated': name,
                      'grade1': removeRedundantSplitpoints(louis.translateString(WORDSPLIT_TABLES_GRADE1, name)),
                      'grade2': removeRedundantSplitpoints(louis.translateString(NAME_WORDSPLIT_TABLES_GRADE2, name)),
                      'type': 2} 
                     for name in names - duplicate_names]
    places = set((place.text.lower() for place in tree.xpath('//brl:place', namespaces=BRL_NAMESPACE)))
    duplicate_places = set((smart_unicode(word.untranslated) for 
                            word in Word.objects.filter(type__in=(3,4)).filter(untranslated__in=places)))
    unknown_places = [{'untranslated': place,
                       'grade1': removeRedundantSplitpoints(louis.translateString(WORDSPLIT_TABLES_GRADE1, place)),
                       'grade2': removeRedundantSplitpoints(louis.translateString(PLACE_WORDSPLIT_TABLES_GRADE2, place)),
                       'type': 4} 
                      for place in places - duplicate_places]
    # filter homographs, names and places from the xml
    xsl = etree.parse(os.path.join(settings.PROJECT_DIR, 'dictionary', 'xslt', 'filter.xsl'))
    transform = etree.XSLT(xsl)
    filtered_tree = transform(tree)
    # grab the rest of the content
    content = etree.tostring(filtered_tree, method="text", encoding=unicode)
    # filter all punctuation and replace dashes by space, so we can split by space below
    content = ''.join(c if unicodedata.category(c) != 'Pd' else ' ' 
                      for c in content 
                      if unicodedata.category(c) in ['Lu', 'Ll', 'Zs', 'Zl', 'Zp', 'Pd']
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
                           word in Word.objects.filter(untranslated__in=new_words)))
    unknown_words = [{'untranslated': word, 
                      'grade1': removeRedundantSplitpoints(louis.translateString(WORDSPLIT_TABLES_GRADE1, word)),
                      'grade2': removeRedundantSplitpoints(louis.translateString(WORDSPLIT_TABLES_GRADE2, word)),
                      'type' : 0} 
                     for word in new_words - duplicate_words]

    unknown_words = unknown_words + unknown_homographs + unknown_names + unknown_places
    unknown_words.sort(cmp=lambda x,y: cmp(x['untranslated'].lower(), y['untranslated'].lower()))

    WordFormSet = modelformset_factory(
        Word, 
        form=RestrictedWordForm,
        exclude=('documents', 'isConfirmed', 'use_for_word_splitting', 'created_at', 'modified_at', 'modified_by'), 
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
        WordFormSet = modelformset_factory(
            Word, 
            form=RestrictedWordForm,
            exclude=('documents', 'isConfirmed', 'use_for_word_splitting', 'created_at', 'modified_at', 'modified_by'), 
            can_delete=True)

        formset = WordFormSet(request.POST, 
                              queryset=Word.objects.filter(documents=document))
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.modified_by = request.user
                instance.save()
            writeLocalTables([document])
            return HttpResponseRedirect(reverse('todo_detail', args=[document_id]))
        else:
            return render_to_response('dictionary/local.html', locals(),
                                      context_instance=RequestContext(request))

    WordFormSet = modelformset_factory(
        Word, 
        form=RestrictedWordForm,
        exclude=('documents', 'isConfirmed', 'use_for_word_splitting', 'created_at', 'modified_at', 'modified_by'), 
        can_delete=True, extra=0)

    formset = WordFormSet(queryset=Word.objects.filter(documents=document).order_by('untranslated', 'type'))

    return render_to_response('dictionary/local.html', locals(), 
                              context_instance=RequestContext(request))


@transaction.commit_on_success
def confirm(request):
    if request.method == 'POST':
        WordFormSet = modelformset_factory(
            Word, 
            form=RestrictedConfirmWordForm,
            exclude=('documents', 'created_at', 'modified_at', 'modified_by'))

        formset = WordFormSet(request.POST, 
                              queryset=Word.objects.filter(isConfirmed=False))
        if formset.is_valid():
            instances = formset.save(commit=False)
            changedDocuments = set()
            for instance in instances:
                instance.modified_by = request.user
                instance.save()
                if instance.isConfirmed and not instance.isLocal:
                    # clear the documents if the word is not local
                    changedDocuments.update(instance.documents.all())
                    instance.documents.clear()
            # write new global white lists
            writeWhiteListTables(Word.objects.filter(isConfirmed=True).filter(isLocal=False).order_by('untranslated'))
            # update local tables
            writeLocalTables(changedDocuments)
            # write new word split table
            writeWordSplitTable(Word.objects.filter(isConfirmed=True).filter(isLocal=False).filter(use_for_word_splitting=True).order_by('untranslated'))
            return HttpResponseRedirect(reverse('todo_index'))
        else:
            return render_to_response('dictionary/confirm.html', locals(),
                                      context_instance=RequestContext(request))

    # create a default for all unconfirmed homographs which have no default, i.e. no restriction word entry
    unconfirmed_homographs = set(Word.objects.filter(type=5).filter(isConfirmed=False).values_list('untranslated', flat=True))
    covered_entries = set(Word.objects.filter(type=0).filter(untranslated__in=unconfirmed_homographs).values_list('untranslated', flat=True))
    for word in unconfirmed_homographs - covered_entries:
        w = Word(untranslated=word, 
                 grade1=removeRedundantSplitpoints(louis.translateString(WORDSPLIT_TABLES_GRADE1, word)),
                 grade2=removeRedundantSplitpoints(louis.translateString(WORDSPLIT_TABLES_GRADE2, word)),
                 type=0,
                 modified_by = request.user)
        w.save()
    
    WordFormSet = modelformset_factory(
        Word, 
        form=RestrictedConfirmWordForm,
        exclude=('documents', 'created_at', 'modified_at', 'modified_by'), extra=0)

    formset = WordFormSet(queryset=Word.objects.filter(isConfirmed=False).order_by('untranslated', 'type'))
    return render_to_response('dictionary/confirm.html', locals(), 
                              context_instance=RequestContext(request))


