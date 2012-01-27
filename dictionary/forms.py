# coding=utf-8
import re

from daisyproducer.dictionary.models import Word

from django.core.exceptions import ValidationError
from django.forms.models import ModelForm
from django.forms.widgets import TextInput
from django.core.validators import RegexValidator

VALID_BRAILLE_RE = re.compile(u"^[A-Z0-9&%[^\],;:/?+=(*).\\\\@#\"!>$_<\'ß§|àáâãåæçèéêëìíîïðñòóôõøùúûýþÿœtwanpkv]+$")
validate = RegexValidator(VALID_BRAILLE_RE, message='Some characters are not valid')

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
            raise ValidationError("Grade1 and Grade2 do not have the same number of hyphenation points")

        return cleaned_data

    def clean_grade1(self):
        data = self.cleaned_data['grade1']
        validate(data)
        return data
        
    def clean_grade2(self):
        data = self.cleaned_data['grade2']
        validate(data)
        return data
        
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

