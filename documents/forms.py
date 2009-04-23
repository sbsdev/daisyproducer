from daisyproducer.documents.external import DaisyPipeline
from daisyproducer.documents.models import Document, Version, Attachment
from daisyproducer.documents.versionHelper import XMLContent
from django import forms
from django.forms import ModelForm
from django.forms.util import ErrorList

class PartialVersionForm(ModelForm):

    def getcontentMetaData(self):
        return self._contentMetaData

    def setcontentMetaData(self, value):
        self._contentMetaData = value

    contentMetaData = property(getcontentMetaData, setcontentMetaData)

    def clean_content(self):
        data = self.files['content']
        # make sure the content has mime type of 'text/xml'
        if data.content_type != 'text/xml':
            raise forms.ValidationError(
                "The mime type of the uploaded file must be 'text/xml'")
        # FIXME: test the mime-type with python-magic
        # make sure the uploaded version is valid xml
        exitMessage = DaisyPipeline.validate(data.temporary_file_path())
        if exitMessage:
            raise forms.ValidationError(
                "The uploaded file is not a valid DTBook XML document: %s" % 
                ' '.join(exitMessage))            
        # make sure the meta data of the uploaded version corresponds
        # to the meta data in the document
        xmlContent = XMLContent()
        errorList = xmlContent.validateContentMetaData(
            data.temporary_file_path(), **self.contentMetaData)
        if errorList:
            raise forms.ValidationError(
                # FIXME: find a way to sanely display all error
                # messages from the errorList, not just the first one
                "The meta data '%s' in the uploaded file does not correspond to the value in the document: '%s' instead of '%s'" % errorList[0])
            
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
            raise forms.ValidationError(
                "The mime type of the uploaded file must be in %s" % 
                ', '.join(choices))
        return data

    class Meta:
        model = Attachment
        fields = ('comment', 'content',)


class PartialDocumentForm(ModelForm):

    def limitChoicesToValidStates(self, document):
        nextValidStateChoices = [(state.id, state.name) for state in document.state.next_states.all()]
        self.fields['state'].choices = nextValidStateChoices

    class Meta:
        model = Document
        fields = ('state',)
    
