from daisyproducer.documents.models import Document, Version, Attachment
from django import forms
from django.forms import ModelForm
from django.forms.util import ErrorList

class DivErrorList(ErrorList):
    def __unicode__(self):
        return self.as_divs()

    def as_divs(self):
        if not self: return u''
        return u'<div class="errorExplanation"><ul>%s</ul></div>' % ''.join([u'<li>%s</li>' % e for e in self])

class BaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(error_class=DivErrorList, *args, **kwargs)

    def as_one_p(self):
        return self._html_output(u'%(label)s %(field)s%(help_text)s', u'%s', '', u' %s', True)


class PartialVersionForm(BaseForm):

    # make sure the content has mime type of 'text/xml'
    def clean_content(self):
        data = self.files['content']
        if data.content_type != 'text/xml':
            raise forms.ValidationError("Uploaded file must be 'text/xml'")
        # FIXME: make sure the uploaded version is valid xml
        return data

    class Meta:
        model = Version
        fields = ('comment', 'content',)

class PartialAttachmentForm(BaseForm):

    @property
    def content_type(self):
        return self.files['content'].content_type

    # make sure the content has mime type as defined in the Attachment class
    def clean_content(self):
        data = self.files['content']
        choices = tuple([choice[0] for choice in Attachment.MIME_TYPE_CHOICES])
        if data.content_type not in choices:
            raise forms.ValidationError("Uploaded file must be in %s" % ', '.join(choices))
        return data

    class Meta:
        model = Attachment
        fields = ('comment', 'content',)


class PartialDocumentForm(BaseForm):

    class Meta:
        model = Document
        fields = ('state',)
    
