# coding=utf-8
import re

from daisyproducer.dictionary.models import Word, LocalWord, GlobalWord
from daisyproducer.dictionary.importExport import findWord, colorDiff, validateBraille, compareBraille

from django import forms

from django.core.exceptions import ValidationError
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.formsets import DELETION_FIELD_NAME
from django.forms.models import ModelForm, BaseModelFormSet
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

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

class PartialGlobalWordForm(ModelForm):
    class Meta:
        model = GlobalWord
        widgets = {}
        # add the title attribute to the widgets
        for field in ('untranslated', 'braille', 'type', 'homograph_disambiguation'):
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
        super(PartialGlobalWordForm, self).__init__(*args, **kwargs)
        if not self.is_bound:
            # make the type field "read-only" (restrict it to a single choice)
            typeChoices = [(id, name) for (id, name) in Word.WORD_TYPE_CHOICES if id == self.initial['type']]
            self.fields['type'].choices = typeChoices
            gradeChoices = [(id, name) for (id, name) in Word.BRAILLE_CONTRACTION_GRADE_CHOICES if id == self.initial['grade']]
            self.fields['grade'].choices = gradeChoices

class BaseConfirmWordForm(forms.Form):
    untranslated = forms.CharField(label=labels['untranslated'], widget=forms.TextInput(attrs={'readonly':'readonly'}))
    braille = forms.CharField(label=labels['braille'], widget=forms.TextInput(attrs={'readonly':'readonly', 'class': 'braille'}))
    type = forms.ChoiceField(label=labels['type'], choices=Word.WORD_TYPE_CHOICES)
    homograph_disambiguation = forms.CharField(label=labels['homograph_disambiguation'], widget=forms.TextInput(attrs={'readonly':'readonly'}), required=False)
    isLocal = forms.BooleanField(label=labels['isLocal'], required=False)

    def __init__(self, *args, **kwargs):
        super(BaseConfirmWordForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'title': field.label})
        if not self.is_bound:
            type_value = self.initial['type']
            homograph_disambiguation_value = self.initial['homograph_disambiguation']
        else:
            type_value = int(self['type'].data)
            homograph_disambiguation_value = self['homograph_disambiguation'].data
        if type_value == 2:
            typeChoices = [(id, name) for (id, name) in Word.WORD_TYPE_CHOICES if id in (1, 2)]
        elif type_value == 4:
            typeChoices = [(id, name) for (id, name) in Word.WORD_TYPE_CHOICES if id in (3, 4)]
        else:
            typeChoices = [(id, name) for (id, name) in Word.WORD_TYPE_CHOICES if id == type_value]
        self.fields['type'].choices = typeChoices
        if type_value == 0:
            self.fields['type'].widget = forms.HiddenInput()
        if homograph_disambiguation_value == '':
            self.fields['homograph_disambiguation'].widget = forms.HiddenInput()

    def clean_braille(self):
        data = self.cleaned_data['braille']
        validate_braille(data)
        return data
    
class ConfirmWordForm(BaseConfirmWordForm):
    isDeferred = forms.BooleanField(label=labels['isDeferred'], required=False)

class ConfirmDeferredWordForm(BaseConfirmWordForm):
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

class GlobalWordBothGradesForm(forms.Form):
    untranslated = forms.CharField(label=labels['untranslated'], widget=forms.TextInput(attrs={'readonly':'readonly'}))
    grade1 = forms.CharField(label=_('Grade 1'), widget=forms.TextInput(attrs={'class': 'braille'}))
    grade2 = forms.CharField(label=_('Grade 2'), widget=forms.TextInput(attrs={'class': 'braille'}))
    original_grade = forms.IntegerField(widget=forms.HiddenInput())
    type = forms.ChoiceField(label=labels['type'], choices=Word.WORD_TYPE_CHOICES)
    homograph_disambiguation = forms.CharField(label=labels['homograph_disambiguation'], widget=forms.TextInput(attrs={'readonly':'readonly'}), required=False)

    def __init__(self, *args, **kwargs):
        super(GlobalWordBothGradesForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'title': field.label})
        if not self.is_bound:
            type_value = self.initial['type']
            homograph_disambiguation_value = self.initial['homograph_disambiguation']
            original_grade = self.initial['original_grade']
        else:
            type_value = int(self['type'].data)
            homograph_disambiguation_value = self['homograph_disambiguation'].data
            original_grade = self['original_grade'].data
        typeChoices = [(id, name) for (id, name) in Word.WORD_TYPE_CHOICES if id == type_value]
        self.fields['type'].choices = typeChoices
        if type_value == 0:
            self.fields['type'].widget = forms.HiddenInput()
        if homograph_disambiguation_value == '':
            self.fields['homograph_disambiguation'].widget = forms.HiddenInput()
        if original_grade == 1:
            self.fields['grade1'].widget.attrs.update({'readonly':'readonly'})
        else:
            self.fields['grade2'].widget.attrs.update({'readonly':'readonly'})

    def clean(self):
        cleaned_data = self.cleaned_data
        original_grade = cleaned_data['original_grade']
        if original_grade == 1:
            validate_braille(cleaned_data['grade2'])
        else:
            validate_braille(cleaned_data['grade1'])
        return cleaned_data
        
class FilterForm(forms.Form):
    filter = forms.CharField(label=_('Filter'), widget=forms.TextInput(attrs={'placeholder': _('Filter...')}), required=False)

class FilterWithGradeForm(FilterForm):
    grade = forms.ChoiceField(label=labels['grade'], choices=(('', _('Any')),) + Word.BRAILLE_CONTRACTION_GRADE_CHOICES, required=False)

class DictionaryUploadForm(forms.Form):
    csv = forms.FileField(
        label = _("CSV File"), 
        help_text = _("CSV File containing global words"))
    
class ColorDiffTextInput(forms.TextInput):
    def render(self, name, value, attrs):
        if self.attrs.has_key('old'):
            diff = u"<span class='diff'>%s</span>" % colorDiff(self.attrs['old'], value,
                                         ("<span class='delete'>", "</span>"), 
                                         ("<span class='insert'>", "</span>"))
        else: diff = ""
        return mark_safe(super(forms.TextInput, self).render(name, value, attrs) + diff)
    
class ImportGlobalWordForm(forms.Form):
    untranslated = forms.CharField(label=labels['untranslated'])
    type = forms.ChoiceField(label=labels['type'], choices=Word.WORD_TYPE_CHOICES)
    grade = forms.ChoiceField(label=labels['grade'], choices=Word.BRAILLE_CONTRACTION_GRADE_CHOICES)
    homograph_disambiguation = forms.CharField(label=labels['homograph_disambiguation'], required=False)
    braille = forms.CharField(label=labels['braille'], widget=ColorDiffTextInput())
    
    def __init__(self, *args, **kwargs):
        super(ImportGlobalWordForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'title': field.label})
        if self.is_bound:
            data = {'untranslated': self['untranslated'].data,
                    'grade': int(self['grade'].data),
                    'type': int(self['type'].data),
                    'homograph_disambiguation': self['homograph_disambiguation'].data,
                    'braille': self['braille'].data}
        else:
            data = self.initial
        self.fields['untranslated'].widget.attrs.update({'readonly': 'readonly'})
        self.fields['homograph_disambiguation'].widget.attrs.update({'readonly': 'readonly'})
        self.fields['type'].choices = [(id, name) for (id, name) in Word.WORD_TYPE_CHOICES if id == data['type']]
        self.fields['grade'].choices = [(id, name) for (id, name) in Word.BRAILLE_CONTRACTION_GRADE_CHOICES if id == data['grade']]
        self.fields['braille'].widget.attrs.update({'class': 'braille'})
        try:
            self.old_braille = findWord(data).braille
            self.fields['braille'].widget.attrs.update({'old': self.old_braille})
        except Exception as e: 
            self.word_not_found_error = e
    
    def clean(self):
        if hasattr(self, 'word_not_found_error'):
            raise ValidationError(self.word_not_found_error)
        return self.cleaned_data
    
    def clean_braille(self):
        data = self.cleaned_data['braille']
        validate_braille(data)
        if hasattr(self, 'old_braille'):
            try:
                compareBraille(data, self.old_braille)
            except Exception as e:
                raise ValidationError(e)
        return data
