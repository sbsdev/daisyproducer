from django import forms
from django.forms.models import BaseModelFormSet
from django.utils.translation import ugettext_lazy as _


class BaseWordFormSet(BaseModelFormSet):
    def add_fields(self, form, index):
        super(BaseWordFormSet, self).add_fields(form, index)
        form.fields["isLocal"] = forms.BooleanField(label=_("Local"), required=False)

