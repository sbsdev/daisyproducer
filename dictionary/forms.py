# coding=utf-8
import re

from daisyproducer.dictionary.models import Word

from django.core.exceptions import ValidationError
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.formsets import DELETION_FIELD_NAME
from django.forms.models import ModelForm, BaseModelFormSet
from django.core.validators import RegexValidator

VALID_BRAILLE_RE = re.compile(u"^[-v]?[A-Z0-9&%[^\],;:/?+=(*).\\\\@#\"!>$_<\'àáâãåæçèéêëìíîïðñòóôõøùúûýþÿœ]+$")
validate_braille = RegexValidator(VALID_BRAILLE_RE, message='Some characters are not valid')
VALID_HOMOGRAPH_RE = re.compile(u"^(|[a-zàáâãåæçèéêëìíîïðñòóôõøùúûýþÿœ]+\|[a-zàáâãåæçèéêëìíîïðñòóôõøùúûýþÿœ]+)$")
validate_homograph = RegexValidator(VALID_HOMOGRAPH_RE, message='Some characters are not valid')

class PartialWordForm(ModelForm):
    class Meta:
        model = Word
        exclude=('document', 'isConfirmed', 'grade'), 
        widgets = {}
        # add the title attribute to the widgets
        for field in ('untranslated', 'braille', 'type', 'homograph_disambiguation', 'isConfirmed', 'isLocal'):
            f = model._meta.get_field(field)
            formField = f.formfield()
            attrs = {'title': formField.label} if field != 'untranslated' else {'title': formField.label, 'readonly': 'readonly'}
            if formField: 
                widgets[field] = type(formField.widget)(attrs=attrs)

    def clean_braille(self):
        data = self.cleaned_data['braille']
        validate_braille(data)
        return data
        
    def clean_homograph_disambiguation(self):
        type = self.cleaned_data.get('type')
        homograph_disambiguation = self.cleaned_data.get('homograph_disambiguation')
        untranslated = self.cleaned_data.get('untranslated')
        if type != 5 and homograph_disambiguation != "":
             raise ValidationError("Should be empty for types other than Homograph")
        if type == 5 and untranslated != homograph_disambiguation.replace('|', ''):
             raise ValidationError("Should the same as untranslated (modulo '|')")
        validate_homograph(homograph_disambiguation)
        return homograph_disambiguation

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
        delete = cleaned_data.get(DELETION_FIELD_NAME)

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

class BaseWordFormSet(BaseModelFormSet):
     def clean(self):
         if any(self.errors):
             return
         unique = True
         words = set()
         msg = "Global words must be unique."
         for i in range(0, self.total_form_count()):
             form = self.forms[i]
             if not form.cleaned_data.get(DELETION_FIELD_NAME):
                 word = (form.cleaned_data['untranslated'], 
                         form.cleaned_data['type'], 
                         form.cleaned_data['homograph_disambiguation'])
                 if word in words:
                     form._errors[NON_FIELD_ERRORS] = form.error_class([msg])
                     unique = False
                 words.add(word)
         if not unique:
             raise ValidationError(msg)
