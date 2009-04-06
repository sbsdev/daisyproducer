from daisyproducer.documents.models import Version, Attachment
from django import forms
from django.forms import ModelForm

class PartialVersionForm(ModelForm):

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

class PartialAttachmentForm(ModelForm):

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


