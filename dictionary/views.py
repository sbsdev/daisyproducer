import louis
from django.forms.models import modelformset_factory
from django.shortcuts import render_to_response

from dictionary.forms import BaseWordFormSet
from dictionary.models import Word


def index(request):
    new_words = sorted([u'regelbasiert', u'Dampfschiff', 
                        u'Kaufmann', u'Wertschriftentransport', u'Spiez', u'liegen'], 
                       key=unicode.lower)
    duplicate_words = [word.untranslated for 
                       word in Word.objects.filter(untranslated__in=new_words)]
    unknown_words = [{'untranslated': word, 
                      'grade1': louis.translateString(['de-ch-g1.ctb'], word.decode('utf-8')).encode('utf-8'),
                      'grade2': louis.translateString(['de-ch-g2.ctb'], word.decode('utf-8')).encode('utf-8')} 
                     for word in new_words if word not in duplicate_words]

    WordFormSet = modelformset_factory(
        Word, exclude=('document', 'isConfirmed'), 
        extra=len(unknown_words), formset=BaseWordFormSet, can_delete=True)

    formset = WordFormSet(queryset=Word.objects.none(), initial=unknown_words)

    return render_to_response('dictionary/index.html', locals())

