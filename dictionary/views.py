import os
import unicodedata
import louis
import codecs
import tempfile

from daisyproducer.dictionary.brailleTables import writeLocalTables, getTables, write_words_with_wrong_default_translation
from daisyproducer.dictionary.forms import RestrictedWordForm, ConfirmWordForm, ConflictingWordForm, ConfirmDeferredWordForm, PartialGlobalWordForm, LookupGlobalWordForm, GlobalWordBothGradesForm, FilterForm, FilterWithGradeForm, DictionaryUploadForm, ImportGlobalWordForm
from daisyproducer.dictionary.models import GlobalWord, LocalWord
from daisyproducer.dictionary.importExport import exportWords, readWord, findWord
from daisyproducer.statistics.models import DocumentStatistic
from daisyproducer.documents.models import Document, State
from daisyproducer.documents.external import saxon9he
from daisyproducer.documents.views.utils import render_to_mimetype_response
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.db.models import Max
from django.forms.models import modelformset_factory
from django.forms.formsets import formset_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.encoding import smart_unicode
from django.contrib.auth.decorators import login_required, permission_required
from collections import defaultdict
from itertools import chain
from lxml import etree

BRL_NAMESPACE = {'brl':'http://www.daisy.org/z3986/2009/braille/'}
MAX_WORDS_PER_PAGE = 25

final_sort_order = State.objects.aggregate(final_sort_order=Max('sort_order')).get('final_sort_order')

@login_required
@transaction.commit_on_success
def check(request, document_id, grade):

    document = get_object_or_404(Document, pk=document_id)

    if request.method == 'POST':
        WordFormSet = modelformset_factory(
            LocalWord, 
            form=RestrictedWordForm,
            exclude=('document', 'isConfirmed', 'isDeferred', 'grade'), 
            can_delete=True)

        formset = WordFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.grade = grade
                instance.document = document
                instance.save()
            writeLocalTables([document])
            redirect = 'dictionary_check_g1' if grade == 1 else 'dictionary_check_g2'
            return HttpResponseRedirect(reverse(redirect, args=[document_id]))
        else:
            return render_to_response('dictionary/words.html', locals(),
                                      context_instance=RequestContext(request))

    # filter some words from the xml
    content = document.latest_version().content
    content.open()
    # strip='none': if this parameter is not set, whitespace is removed automatically for documents with a DOCTYPE declaration
    tree = etree.parse(saxon9he(content.file, os.path.join(settings.PROJECT_DIR, 'dictionary', 'xslt', 'filter.xsl'), '-strip:none', contraction=grade).stdout)
    content.close()

    # grab the homographs
    homographs = set(("|".join(homograph.xpath('text()')).lower() 
                      for homograph in tree.xpath('//brl:homograph', namespaces=BRL_NAMESPACE)))
    duplicate_homographs = set((smart_unicode(word) for 
                                word in 
                                chain(GlobalWord.objects.filter(grade=grade).filter(type=5).filter(homograph_disambiguation__in=homographs).values_list('homograph_disambiguation', flat=True),
                                      LocalWord.objects.filter(grade=grade).filter(type=5).filter(document=document).filter(homograph_disambiguation__in=homographs).values_list('homograph_disambiguation', flat=True))))
    unknown_homographs = [{'untranslated': homograph.replace('|', ''), 
                           'braille': louis.translateString(getTables(grade), homograph.replace('|', unichr(0x250A))),
                           'type': 5,
                           'homograph_disambiguation': homograph}
                          for homograph in homographs - duplicate_homographs]
    # grab names and places
    names = set((name for names in 
                 (name.text.lower().split() for name in tree.xpath('//brl:name', namespaces=BRL_NAMESPACE) if name.text != None) for name in names))
    duplicate_names = set((smart_unicode(word) for 
                           word in 
                           chain(GlobalWord.objects.filter(grade=grade).filter(type__in=(1,2)).filter(untranslated__in=names).values_list('untranslated', flat=True),
                                 LocalWord.objects.filter(grade=grade).filter(type__in=(1,2)).filter(document=document).filter(untranslated__in=names).values_list('untranslated', flat=True))))
    unknown_names = [{'untranslated': name, 
                      'braille': louis.translateString(getTables(grade, name=True), name), 
                      'type': 2,
                      'homograph_disambiguation': ''}
                     for name in names - duplicate_names]
    places = set((place for places in 
                 (place.text.lower().split() for place in tree.xpath('//brl:place', namespaces=BRL_NAMESPACE) if place.text != None) for place in places))
    duplicate_places = set((smart_unicode(word) for 
                            word in 
                            chain(GlobalWord.objects.filter(grade=grade).filter(type__in=(3,4)).filter(untranslated__in=places).values_list('untranslated', flat=True),
                                  LocalWord.objects.filter(grade=grade).filter(type__in=(3,4)).filter(document=document).filter(untranslated__in=places).values_list('untranslated', flat=True))))
    unknown_places = [{'untranslated': place,
                       'braille': louis.translateString(getTables(grade, place=True), place),
                       'type': 4,
                       'homograph_disambiguation': ''}
                      for place in places - duplicate_places]

    # filter homographs, names and places from the xml
    xsl = etree.parse(os.path.join(settings.PROJECT_DIR, 'dictionary', 'xslt', 'filter_names.xsl'))
    transform = etree.XSLT(xsl)
    filtered_tree = transform(tree)
    # grab the rest of the content
    content = etree.tostring(filtered_tree, method="text", encoding=unicode)
    # filter all punctuation and replace dashes by space, so we can split by space below
    content = ''.join(
        # replace Punctuation Dash and Punctuation other (except for "'") with space
        c if c == u"\u0027" or unicodedata.category(c) not in ['Pd', 'Po'] else ' '
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
    duplicate_words = set((smart_unicode(word) for 
                           word in 
                           chain(GlobalWord.objects.filter(grade=grade).filter(untranslated__in=new_words).values_list('untranslated', flat=True),
                                 LocalWord.objects.filter(grade=grade).filter(document=document).filter(untranslated__in=new_words).values_list('untranslated', flat=True))))
    unknown_words = [{'untranslated': word, 
                      'braille': louis.translateString(getTables(grade), word),
                      'type' : 0,
                      'homograph_disambiguation': ''}
                     for word in new_words - duplicate_words]

    unknown_words = unknown_words + unknown_homographs + unknown_names + unknown_places
    unknown_words.sort(cmp=lambda x,y: cmp(x['untranslated'].lower(), y['untranslated'].lower()))

    # remove words from the local words which are no longer in the document (they might have
    # been typos that slipped in to the local words and were corrected subsequently)
    all_duplicates = duplicate_homographs | duplicate_names | duplicate_places | duplicate_words
    LocalWord.objects.filter(grade=grade, document=document).exclude(untranslated__in=all_duplicates).delete()

    paginator = Paginator(unknown_words, MAX_WORDS_PER_PAGE)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    
    try:
        words = paginator.page(page)
    except InvalidPage:
        words = paginator.page(paginator.num_pages)

    WordFormSet = modelformset_factory(
        LocalWord, 
        form=RestrictedWordForm,
        exclude=('document', 'isConfirmed', 'isDeferred', 'grade'), 
        extra=len(words.object_list), can_delete=True)

    have_type = any((word['type']!=0 for word in words.object_list))
    have_homograph_disambiguation = any((word['homograph_disambiguation']!='' for word in words.object_list))
    formset = WordFormSet(queryset=LocalWord.objects.none(), initial=words.object_list)

    # Document statistic
    stats = DocumentStatistic(document=document, grade=grade, total=len(new_words), unknown=len(unknown_words))
    percentage = 100.0*stats.unknown/stats.total
    stats.save()

    return render_to_response('dictionary/words.html', locals(),
                              context_instance=RequestContext(request))

@login_required
@transaction.commit_on_success
def local(request, document_id, grade):

    document = get_object_or_404(Document, pk=document_id)
    if request.method == 'POST':
        WordFormSet = modelformset_factory(
            LocalWord, 
            form=RestrictedWordForm,
            exclude=('document', 'isConfirmed', 'isDeferred', 'grade'), 
            can_delete=True)

        formset = WordFormSet(request.POST, 
                              queryset=LocalWord.objects.filter(grade=grade, document=document))
        if formset.is_valid():
            instances = formset.save()
            writeLocalTables([document])
            redirect = 'dictionary_local_g1' if grade == 1 else 'dictionary_local_g2'
            return HttpResponseRedirect(reverse(redirect, args=[document_id]))
        else:
            return render_to_response('dictionary/local.html', locals(),
                                      context_instance=RequestContext(request))

    filterform = FilterForm(request.GET)
    if filterform.is_valid():
        currentFilter = filterform.cleaned_data['filter']
    
    words_list = LocalWord.objects.filter(grade=grade, document=document,
                                          untranslated__contains=currentFilter).order_by('untranslated', 'type')
    paginator = Paginator(words_list, MAX_WORDS_PER_PAGE)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    
    try:
        words = paginator.page(page)
    except InvalidPage:
        words = paginator.page(paginator.num_pages)

    WordFormSet = modelformset_factory(
        LocalWord, 
        form=RestrictedWordForm,
        exclude=('document', 'isConfirmed', 'isDeferred', 'grade'), 
        can_delete=True, extra=0)

    formset = WordFormSet(queryset=words.object_list)

    return render_to_response('dictionary/local.html', locals(), 
                              context_instance=RequestContext(request))

def update_word_tables(form, grade, deferred):
    filter_args = dict((k, form.cleaned_data[k]) for k in ('untranslated', 'type', 'homograph_disambiguation'))
    if not deferred and form.cleaned_data['isDeferred']:
        LocalWord.objects.filter(grade=grade, **filter_args).update(isDeferred=True, isLocal=form.cleaned_data['isLocal'])
    elif form.cleaned_data['isLocal']:
        LocalWord.objects.filter(grade=grade, **filter_args).update(isConfirmed=True, isLocal=True, 
                                                                    braille=form.cleaned_data['braille'], isDeferred=False)
    else:
        # move confirmed and non-local words to the global dictionary
        GlobalWord.objects.create(grade=grade, braille=form.cleaned_data['braille'], **filter_args)
        # delete all entries from the LocalWord table
        LocalWord.objects.filter(grade=grade, **filter_args).delete()
    
@login_required
@permission_required("dictionary.add_globalword")
@transaction.commit_on_success
def confirm(request, grade, deferred=False):
    if [word for word in get_conflicting_words(grade)]:
        redirect = ('dictionary_confirm_deferred_conflicting_duplicates_g' if deferred
                        else 'dictionary_confirm_conflicting_duplicates_g') + str(grade)
        return HttpResponseRedirect(reverse(redirect))

    WordFormSet = formset_factory(ConfirmDeferredWordForm if deferred else ConfirmWordForm, extra=0) 
    if request.method == 'POST':

        formset = WordFormSet(request.POST)
        if formset.is_valid():
            # FIXME: in Djano 1.3+ formset formmsets are iterable, so you can just say 
            # for form in formset:
            for form in formset.forms:
                update_word_tables(form, grade, deferred)
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
            # redirect to self as there might be more words
            redirect = ('dictionary_confirm_deferred_g' if deferred else 'dictionary_confirm_g') + str(grade)
            return HttpResponseRedirect(reverse(redirect))
        else:
            return render_to_response('dictionary/confirm.html', locals(),
                                      context_instance=RequestContext(request))

    # create a default for all unconfirmed homographs which have no default, i.e. no restriction word entry
    unconfirmed_homographs = set((smart_unicode(word) for 
                                  word in 
                                  LocalWord.objects.filter(grade=grade, type=5, isConfirmed=False, isDeferred=deferred, 
                                                           document__state__sort_order=final_sort_order).values_list('untranslated', flat=True)))
    if unconfirmed_homographs:
        covered_entries = set((smart_unicode(word) for 
                               word in 
                               chain(
                    LocalWord.objects.filter(grade=grade, type=0, untranslated__in=unconfirmed_homographs).values_list('untranslated', flat=True),
                    GlobalWord.objects.filter(grade=grade, type=0, untranslated__in=unconfirmed_homographs).values_list('untranslated', flat=True))))
                                 
        for word in unconfirmed_homographs - covered_entries:
            document = Document.objects.filter(localword__grade=grade, localword__type=5, localword__isConfirmed=False, localword__untranslated=word)[0]
            w = LocalWord(untranslated=word, 
                          braille=louis.translateString(getTables(grade), word),
                          grade=grade, type=0, document=document)
            w.save()
    
    filterform = FilterForm(request.GET)
    if filterform.is_valid():
        currentFilter = filterform.cleaned_data['filter']
    
    words_to_confirm = LocalWord.objects.filter(grade=grade, isConfirmed=False, isDeferred=deferred, 
                                                untranslated__contains=currentFilter,
                                                document__state__sort_order=final_sort_order).order_by('untranslated', 'type').values('untranslated', 'braille', 'type', 'homograph_disambiguation', 'isLocal').distinct()
    paginator = Paginator(words_to_confirm, MAX_WORDS_PER_PAGE)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    
    try:
        words = paginator.page(page)
    except InvalidPage:
        words = paginator.page(paginator.num_pages)

    have_type = any((word['type']!=0 for word in words.object_list))
    have_homograph_disambiguation = any((word['homograph_disambiguation']!='' for word in words.object_list))
    formset = WordFormSet(initial=words.object_list)
    return render_to_response('dictionary/confirm.html', locals(),
                              context_instance=RequestContext(request))

def get_conflicting_words(grade):
    from django.db import connection, transaction
    cursor = connection.cursor()
    DETECT_CONFLICTING_WORDS = """
SELECT DISTINCT word_a.untranslated, word_a.type, word_a.homograph_disambiguation, word_a.braille, 0
FROM dictionary_localword AS word_a, dictionary_localword AS word_b, documents_document AS doc_a, documents_document AS doc_b
WHERE word_a.untranslated = word_b.untranslated 
AND word_a.type = word_b.type 
AND word_a.homograph_disambiguation = word_b.homograph_disambiguation 
AND word_a.grade = %s
AND word_a.grade = word_b.grade
AND word_a.braille != word_b.braille
AND word_a.document_id=doc_a.id
AND word_b.document_id=doc_b.id
AND doc_a.state_id=%s
AND doc_b.state_id=%s
UNION
SELECT DISTINCT word_a.untranslated, word_a.type, word_a.homograph_disambiguation, word_a.braille, 0
FROM dictionary_localword AS word_a, dictionary_globalword AS word_b, documents_document AS doc_a
WHERE word_a.untranslated = word_b.untranslated 
AND word_a.type = word_b.type 
AND word_a.homograph_disambiguation = word_b.homograph_disambiguation 
AND word_a.grade = %s
AND word_a.grade = word_b.grade
AND word_a.braille != word_b.braille
AND word_a.document_id=doc_a.id
AND doc_a.state_id=%s
UNION
SELECT word_a.untranslated, word_a.type, word_a.homograph_disambiguation, word_b.braille, word_b.id
FROM dictionary_localword AS word_a, dictionary_globalword AS word_b, documents_document AS doc_a
WHERE word_a.untranslated = word_b.untranslated 
AND word_a.type = word_b.type 
AND word_a.homograph_disambiguation = word_b.homograph_disambiguation 
AND word_a.grade = %s
AND word_a.grade = word_b.grade
AND word_a.braille != word_b.braille
AND word_a.document_id=doc_a.id
AND doc_a.state_id=%s"""
    cursor.execute(DETECT_CONFLICTING_WORDS, [grade, final_sort_order, final_sort_order, grade, final_sort_order, grade, final_sort_order])
    return cursor.fetchall()

@login_required
@permission_required("dictionary.add_globalword")
@transaction.commit_on_success
def confirm_conflicting_duplicates(request, grade, deferred=False):

    WordFormSet = formset_factory(ConflictingWordForm, extra=0)
    if request.method == 'POST':
        formset = WordFormSet(request.POST)
        if formset.is_valid():
            affected_documents = set()
            # save the correct words in the GlobalWord
            # FIXME: in Djano 1.3+ formset formmsets are iterable, so you can just say 
            # for form in formset:
            for form in formset.forms:
                # FIXME: This is an open attack vector. A user can
                # change any word in the global dict with a carefuly
                # crafted post. It might be better not to pass the id.
                word = GlobalWord(grade=grade, **form.cleaned_data)
                word.save()
                # note which documents are affected
                filter_args = dict((k, form.cleaned_data[k]) for k in ('untranslated', 'type', 'homograph_disambiguation'))
                words_to_delete = LocalWord.objects.filter(grade=grade, **filter_args)
                affected_documents.update([word.document for word in words_to_delete])
                # delete the conflicting words (and also plain
                # duplicate non-conflicting words) from the LocalWords
                words_to_delete.delete()
            writeLocalTables(list(affected_documents))
            # once we are done dealing with conflicts we go back to regular confirmation
            redirect = 'dictionary_confirm_g1' if grade == 1 else 'dictionary_confirm_g2'
            return HttpResponseRedirect(reverse(redirect))
    else:
        conflicting_words = get_conflicting_words(grade)
        braille_choices = defaultdict(set)
        global_ids = defaultdict()
        for untranslated, type, homograph_disambiguation, braille, global_id in conflicting_words:
            key = (untranslated, type, homograph_disambiguation)
            braille_choices[key].update([braille])
            if global_id > 0:
                global_ids[key] = global_id

        initial=[
            {'id': global_ids.get((untranslated, type, homograph_disambiguation)),
             'untranslated': untranslated,
             'type': type,
             'homograph_disambiguation': homograph_disambiguation,
             'braille': sorted(braille_choices[(untranslated, type, homograph_disambiguation)]),
             } for untranslated, type, homograph_disambiguation in braille_choices.keys()]
        initial = sorted(initial, key=lambda x: x['untranslated'])
        
        WordFormSet = formset_factory(ConflictingWordForm, extra=0)
        formset = WordFormSet(initial=initial)

    return render_to_response('dictionary/confirm_conflicting_duplicates.html', locals(), 
                              context_instance=RequestContext(request))

@login_required
@permission_required("dictionary.add_globalword")
@transaction.commit_on_success
def confirm_single(request, grade, deferred=False):
    try:
        # just get one word
        words = LocalWord.objects.filter(grade=grade).filter(isConfirmed=False, isDeferred=deferred, 
                                                            document__state__sort_order=final_sort_order)
        word = words.order_by('untranslated', 'type')[0:1].get()
    except LocalWord.DoesNotExist:
        return HttpResponseRedirect(reverse('todo_index'))

    if request.method == 'POST':
        form =  ConfirmDeferredWordForm(request.POST) if deferred else ConfirmWordForm(request.POST)
        if form.is_valid():
            update_word_tables(form, grade, deferred)

            # redirect to self to deal with the next word
            redirect = ('dictionary_single_confirm_deferred_g' if deferred else 'dictionary_single_confirm_g') + str(grade)
            return HttpResponseRedirect(reverse(redirect))
        else:
            return render_to_response('dictionary/confirm_single.html', locals(),
                                      context_instance=RequestContext(request))

    initial={'untranslated': word.untranslated,
             'type': word.type,
             'homograph_disambiguation': word.homograph_disambiguation,
             'braille': word.braille,
             'isLocal': word.isLocal}
        
    form = ConfirmDeferredWordForm(initial=initial) if deferred else ConfirmWordForm(initial=initial)
    return render_to_response('dictionary/confirm_single.html', locals(), 
                              context_instance=RequestContext(request))

@login_required
@transaction.commit_on_success
def edit_global_words(request, read_only):

    read_only = read_only or not request.user.has_perm("dictionary.change_globalword")
    WordFormSet = modelformset_factory(GlobalWord, extra=0, form=LookupGlobalWordForm if read_only else PartialGlobalWordForm)
    
    if request.method == 'POST':
        if read_only:
            return HttpResponse("You don't have the right permissions")
        formset = WordFormSet(request.POST)
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(reverse('todo_index'))
        else:
            return render_to_response('dictionary/edit_globals.html', locals(),
                                      context_instance=RequestContext(request))

    filterform = FilterWithGradeForm(request.GET)
    if filterform.is_valid():
        currentFilter = filterform.cleaned_data['filter']
        currentGrade = filterform.cleaned_data['grade']

    filter_args = {}
    for key, value in [('untranslated__contains', currentFilter), ('grade', currentGrade)]:
        if value:
            filter_args[key] = value

    words_to_edit = GlobalWord.objects.filter(**filter_args).order_by('untranslated', 'type')
    paginator = Paginator(words_to_edit, MAX_WORDS_PER_PAGE)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    
    try:
        words = paginator.page(page)
    except InvalidPage:
        words = paginator.page(paginator.num_pages)

    have_type = any((word.type != 0 for word in words.object_list))
    have_homograph_disambiguation = any((word.homograph_disambiguation != '' for word in words.object_list))
    formset = WordFormSet(queryset=words.object_list)
    return render_to_response('dictionary/edit_globals.html', locals(),
                              context_instance=RequestContext(request))

@login_required
@permission_required("dictionary.change_globalword")
@transaction.commit_on_success
def edit_global_words_with_missing_braille(request):

    WordFormSet = formset_factory(GlobalWordBothGradesForm, extra=0)

    if request.method == 'POST':
        formset = WordFormSet(request.POST)
        if formset.is_valid():
            for form in formset.forms:
                GlobalWord.objects.create(
                    untranslated=form.cleaned_data['untranslated'], 
                    braille=form.cleaned_data['grade2'] if form.cleaned_data['original_grade'] == 1 else form.cleaned_data['grade1'],
                    grade=2 if form.cleaned_data['original_grade'] == 1 else 1,
                    type=form.cleaned_data['type'],
                    homograph_disambiguation=form.cleaned_data['homograph_disambiguation'])
            return HttpResponseRedirect(reverse('todo_index'))
        else:
            return render_to_response('dictionary/edit_missing_globals.html', locals(),
                                      context_instance=RequestContext(request))

    WORDS_WITH_MISSING_BRAILLE = """
SELECT l.* 
FROM dictionary_globalword AS l
WHERE NOT EXISTS
      (
      SELECT NULL
      FROM dictionary_globalword AS r
      WHERE
	l.untranslated = r.untranslated AND 
      	l.type = r.type AND
      	l.homograph_disambiguation = r.homograph_disambiguation AND
      	l.grade != r.grade
      )
ORDER BY l.grade, l.untranslated
"""
    single_grade_words = GlobalWord.objects.raw(WORDS_WITH_MISSING_BRAILLE)
    missing_words = [{'untranslated': smart_unicode(word.untranslated),
                      'original_grade': word.grade,
                      'grade1': smart_unicode(word.braille) if word.grade == 1 else louis.translateString(getTables(1), smart_unicode(word.untranslated)),
                      'grade2': smart_unicode(word.braille) if word.grade == 2 else louis.translateString(getTables(2), smart_unicode(word.untranslated)),
                      'type' : word.type,
                      'homograph_disambiguation': smart_unicode(word.homograph_disambiguation)}
                     for word in single_grade_words]

    paginator = Paginator(missing_words, MAX_WORDS_PER_PAGE)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    
    try:
        words = paginator.page(page)
    except InvalidPage:
        words = paginator.page(paginator.num_pages)

    formset = WordFormSet(initial=words.object_list)
    return render_to_response('dictionary/edit_missing_globals.html', locals(),
                              context_instance=RequestContext(request))

def export_words(request):
    if request.method == 'GET':
        tmp = tempfile.NamedTemporaryFile(prefix="daisyproducer-", suffix=".csv", delete=False)
        tmp.close() # we are only interested in a unique filename
        f = codecs.open(tmp.name, "w", "utf-8")
        exportWords(f)
        f.close()
        return render_to_mimetype_response('text/csv', 'Global dictionary dump', tmp.name)

@login_required
@permission_required("dictionary.change_globalword")
def upload_words(request):
    if request.method != 'POST':
        form = DictionaryUploadForm()
        return render_to_response('dictionary/upload.html', locals(), 
                                  context_instance=RequestContext(request))
    form = DictionaryUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return render_to_response('dictionary/upload.html', locals(), 
                                  context_instance=RequestContext(request))
    f = codecs.open(request.FILES['csv'].temporary_file_path(), "r", "utf-8")
    initial = []
    try:
        lineNo = 0
        for line in f.read().splitlines():
            lineNo += 1
            for word in readWord(line):
                try:
                    if word['braille'] == findWord(word).braille: continue
                except: pass
                initial.append(word)
    except Exception as e:
        return render_to_response('error.html', {'message': "%s (line %d)" % (str(e), lineNo), 'code': line})
    finally:
        f.close()
    ImportGlobalWordFormset = formset_factory(ImportGlobalWordForm, extra=0)
    formset = ImportGlobalWordFormset(initial=initial)
    return render_to_response('dictionary/import.html', locals(), context_instance=RequestContext(request))

def import_words(request):
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('dictionary_upload'))
    ImportGlobalWordFormset = formset_factory(ImportGlobalWordForm)
    formset = ImportGlobalWordFormset(request.POST)
    if not formset.is_valid():
        return render_to_response('dictionary/import.html', locals(),
                                  context_instance=RequestContext(request))
    for form in formset.forms:
        word = form.cleaned_data
        oldWord = findWord(word)
        oldWord.braille = word['braille']
        oldWord.save()
        return HttpResponseRedirect(reverse('todo_index'))

@login_required
@permission_required("dictionary.change_globalword")
def words_with_wrong_default_translation(request):
    words = GlobalWord.objects.order_by('untranslated')
    return render_to_mimetype_response(
        'text/csv', 
        'Global words with wrong rule based translation', 
        write_words_with_wrong_default_translation(words))


