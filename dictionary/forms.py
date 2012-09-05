# coding=utf-8
import re

from daisyproducer.dictionary.models import Word, LocalWord

from django import forms

from django.core.exceptions import ValidationError
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.formsets import DELETION_FIELD_NAME
from django.forms.models import ModelForm, BaseModelFormSet
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

VALID_BRAILLE_RE = re.compile(u"^([-]|[-]?[A-Z0-9&%[^\],;:/?+=(*).\\\\@#\"!>$_<\'àáâãåæçèéêëìíîïðñòóôõøùúûýþÿœāăąćĉċčďđēėęğģĥħĩīįıĳĵķĺļľŀłńņňŋōŏőŕŗřśŝşšţťŧũūŭůűųŵŷźżžǎẁẃẅỳ]+)$")
validate_braille = RegexValidator(VALID_BRAILLE_RE, message='Some characters are not valid')
VALID_HOMOGRAPH_RE = re.compile(u"^(|\\w+\\|\\w+)$", re.UNICODE)
validate_homograph = RegexValidator(VALID_HOMOGRAPH_RE, message='Some characters are not valid')

labels = dict([(name, LocalWord._meta.get_field(name).verbose_name) for name in LocalWord._meta.get_all_field_names()])

class PartialWordForm(ModelForm):
    class Meta:
        model = LocalWord
        exclude=('document', 'isConfirmed', 'grade')
        widgets = {}
        # add the title attribute to the widgets
        for field in ('untranslated', 'braille', 'type', 'homograph_disambiguation', 'isConfirmed', 'isLocal'):
            f = model._meta.get_field(field)
            formField = f.formfield()
            if formField:
                attrs = {'title': formField.label}
                if field == 'braille':
                    attrs.update({'class': 'braille'})
                elif field in ('untranslated', 'homograph_disambiguation'):
                    attrs.update({'readonly': 'readonly'})
                widgets[field] = type(formField.widget)(attrs=attrs)

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        if not self.is_bound:
            # make the type field "read-only" (restrict it to a single choice)
            typeChoices = [(id, name) for (id, name) in Word.WORD_TYPE_CHOICES if id == self.initial['type']]
            self.fields['type'].choices = typeChoices
            if self.initial['type'] == 0:
                self.fields['type'].widget = forms.HiddenInput()
            if self.initial['homograph_disambiguation'] == '':
                self.fields['homograph_disambiguation'].widget = forms.HiddenInput()

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
    # only clean if a word is not ignored
    def clean(self):
        cleaned_data = self.cleaned_data
        delete = cleaned_data.get(DELETION_FIELD_NAME)

        if not delete:
            return super(RestrictedWordForm, self).clean()

        return cleaned_data

# class RestrictedConfirmWordForm(PartialWordForm):
#     def __init__(self, *args, **kwargs):
#         super(RestrictedConfirmWordForm, self).__init__(*args, **kwargs)
#         if not self.is_bound:
#             if self.initial['type'] == 0:
#                 typeChoices = [(id, name) for (id, name) in Word.WORD_TYPE_CHOICES if id in (0, 1, 2, 3, 4)]
#             elif self.initial['type'] == 2:
#                 typeChoices = [(id, name) for (id, name) in Word.WORD_TYPE_CHOICES if id in (1, 2)]
#             elif self.initial['type'] == 4:
#                 typeChoices = [(id, name) for (id, name) in Word.WORD_TYPE_CHOICES if id in (3, 4)]
#             else:
#                 typeChoices = [(id, name) for (id, name) in Word.WORD_TYPE_CHOICES if id == self.initial['type']]
#             self.fields['type'].choices = typeChoices

#     # only clean if a word is confirmed
#     def clean(self):
#         cleaned_data = self.cleaned_data
#         isConfirmed = cleaned_data.get("isConfirmed")

#         if isConfirmed:
#             return super(RestrictedConfirmWordForm, self).clean()

#         return cleaned_data

class ConfirmSingleWordForm(forms.Form):
    untranslated = forms.CharField(label=labels['untranslated'], widget=forms.TextInput(attrs={'readonly':'readonly'}))
    braille = forms.CharField(label=labels['braille'], widget=forms.TextInput(attrs={'readonly':'readonly', 'class': 'braille'}))
    type = forms.ChoiceField(label=labels['type'], choices=Word.WORD_TYPE_CHOICES)
    homograph_disambiguation = forms.CharField(label=labels['homograph_disambiguation'], widget=forms.TextInput(attrs={'readonly':'readonly'}), required=False)
    isLocal = forms.BooleanField(label=labels['isLocal'], required=False)

    def __init__(self, *args, **kwargs):
        super(ConfirmSingleWordForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'title': field.label})
        if not self.is_bound:
            if self.initial['type'] == 2:
                typeChoices = [(id, name) for (id, name) in Word.WORD_TYPE_CHOICES if id in (1, 2)]
            elif self.initial['type'] == 4:
                typeChoices = [(id, name) for (id, name) in Word.WORD_TYPE_CHOICES if id in (3, 4)]
            else:
                typeChoices = [(id, name) for (id, name) in Word.WORD_TYPE_CHOICES if id == self.initial['type']]
            self.fields['type'].choices = typeChoices
            if self.initial['type'] == 0:
                self.fields['type'].widget = forms.HiddenInput()
            if self.initial['homograph_disambiguation'] == '':
                self.fields['homograph_disambiguation'].widget = forms.HiddenInput()

class ConfirmWordForm(ConfirmSingleWordForm):
    isDeferred = forms.BooleanField(label=labels['isDeferred'], required=False)

class ConfirmDeferredWordForm(ConfirmSingleWordForm):
    braille = forms.CharField(label=labels['braille'], widget=forms.TextInput(attrs={'class': 'braille'}))

class ConflictingWordForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    untranslated = forms.CharField(label=labels['untranslated'], widget=forms.TextInput(attrs={'readonly':'readonly'}))
    braille = forms.CharField(label=labels['braille'], widget=forms.Select())
    type = forms.ChoiceField(label=labels['type'], choices=Word.WORD_TYPE_CHOICES)
    homograph_disambiguation = forms.CharField(label=labels['homograph_disambiguation'], widget=forms.TextInput(attrs={'readonly':'readonly'}), required=False)

    def __init__(self, *args, **kwargs):
        super(ConflictingWordForm, self).__init__(*args, **kwargs)
        if not self.is_bound:
            brailleChoices = [(braille, braille) for braille in self.initial['braille']]
            self.fields['braille'].widget.choices = brailleChoices
            typeChoices = [(id, name) for (id, name) in Word.WORD_TYPE_CHOICES if id == self.initial['type']]
            self.fields['type'].choices = typeChoices

