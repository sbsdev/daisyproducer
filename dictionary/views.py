import string

import louis
from django.forms.models import modelformset_factory
from django.shortcuts import render_to_response, get_object_or_404
from lxml import etree

from dictionary.forms import BaseWordFormSet
from dictionary.models import Word
from documents.models import Document


def dictionary(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    document.latest_version().content.open()
    tree = etree.parse(document.latest_version().content.file)
    document.latest_version().content.close()
    content = etree.tostring(tree, method="text", encoding=unicode)
    punctuation = u'!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\u2039\u203A\u00AB\u00BB' # left/right pointing (single) guillemet
    translation_table = dict((ord(char), None) for char in punctuation)
    content = content.translate(translation_table)
    new_words = {}
    for word in content.split():
        new_words[word] = 1
    duplicate_words = [word.untranslated for 
                       word in Word.objects.filter(untranslated__in=new_words.keys())]
    unknown_words = [{'untranslated': word, 
                      'grade1': louis.translateString(['de-ch-g1.ctb'], word),
                      'grade2': louis.translateString(['de-ch-g2.ctb'], word)} 
                     for word in new_words if word not in duplicate_words]

    WordFormSet = modelformset_factory(
        Word, exclude=('document', 'isConfirmed'), 
        extra=len(unknown_words), formset=BaseWordFormSet, can_delete=True)

    formset = WordFormSet(queryset=Word.objects.none(), initial=unknown_words)

    return render_to_response('dictionary/index.html', locals())

