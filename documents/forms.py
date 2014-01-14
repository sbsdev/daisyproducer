from daisyproducer.documents.external import DaisyPipeline
from daisyproducer.documents.models import Document, Version, Attachment, LargePrintProfile, Image
from daisyproducer.documents.versionHelper import XMLContent
from django import forms
from django.core.files.base import ContentFile
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
import tempfile
import os
from lxml import etree
from django.forms.models import model_to_dict

def validate_content(fileName, contentMetaData, removeFile=False):
    # make sure the uploaded version is valid xml
    exitMessages = DaisyPipeline.validate(fileName)
    if exitMessages:
        if removeFile:
            os.remove(fileName)
        raise forms.ValidationError(
            ["The uploaded file is not a valid DTBook XML document: "] + 
            exitMessages)            
    # make sure the meta data of the uploaded version corresponds
    # to the meta data in the document
    xmlContent = XMLContent()
    try:
        errorList = xmlContent.validateContentMetaData(fileName , **contentMetaData)
    except etree.XMLSyntaxError as e:
        raise forms.ValidationError(("The uploaded file is not a valid DTBook XML document:" + e.message))
    if removeFile:
        os.remove(fileName)
    if errorList:
        raise forms.ValidationError(
            map(lambda errorTuple : 
                "The meta data '%s' in the uploaded file does not correspond to the value in the document: '%s' instead of '%s'" % errorTuple, 
                errorList))


class PartialVersionForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.contentMetaData = kwargs.pop('contentMetaData', None)
        super(PartialVersionForm, self).__init__(*args, **kwargs) 

    def clean_content(self):
        data = self.files['content']
        # make sure the content has mime type of 'text/xml'
        if data.content_type != 'text/xml':
            raise forms.ValidationError(
                "The mime type of the uploaded file must be 'text/xml'")
        # FIXME: test the mime-type with python-magic
        # make sure the uploaded version is valid xml
        validate_content(data.temporary_file_path(), self.contentMetaData)
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

class PartialImageForm(ModelForm):

    # make sure the content has mime type as defined in the Image class
    def clean_content(self):
        data = self.files['content']
        choices = tuple([choice[0] for choice in Image.MIME_TYPE_CHOICES])
        if data.content_type not in choices:
            raise forms.ValidationError(
                "The mime type of the uploaded file must be in %s" % 
                ', '.join(choices))
        return data

    class Meta:
        model = Image
        fields = ('content',)

class PartialDocumentForm(ModelForm):

    def limitChoicesToValidStates(self, document):
        nextValidStateChoices = [(state.id, state.name) for state in document.state.next_states.all()]
        self.fields['state'].choices = nextValidStateChoices

    class Meta:
        model = Document
        fields = ('state',)
    
class OCRForm(forms.Form):
    data = forms.FileField(
        label = _("Data from scan"), 
        help_text = _("The image files that resulted from the scan"))


class MarkupForm(forms.Form):
    data = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class' : "wiki-edit",
                'cols' : "60",
                'rows' : "24"}))
    comment = forms.CharField(
        widget=forms.TextInput(attrs={'size':'60'}))

    def __init__(self, *args, **kwargs):
        self.document = kwargs.pop('document', None)
        self.user = kwargs.pop('user', None)
        super(MarkupForm, self).__init__(*args, **kwargs) 

    def clean_data(self):
        data = self.cleaned_data['data']
        tmpFile, tmpFileName = tempfile.mkstemp(prefix="daisyproducer-", suffix=".xml")
        tmpFile = os.fdopen(tmpFile,'w')
        tmpFile.write(data.encode('utf-8'))
        tmpFile.close()
        # make sure the uploaded version is valid xml
        validate_content(tmpFileName, model_to_dict(self.document), True)
        return data

    def save(self):
        # create a new version with the new content
        contentString = self.cleaned_data['data']
        content = ContentFile(contentString.encode("utf-8"))
        version = Version.objects.create(
            comment = self.cleaned_data['comment'],
            document = self.document,
            created_by = self.user)
        version.content.save("updated_version.xml", content)


class SBSFormForm(forms.Form):
    BRAILLE_CONTRACTION_GRADE_CHOICES = (
        ('0', _('Grade 0')),
        ('1', _('Grade 1')),
        ('2', _('Grade 2')),
        )
    BRAILLE_ACCENTS_CHOICES = (
        ('de-accents', _('All Accents Detailed')),
        ('de-accents-reduced', _('All Accents Reduced')),
        ('de-accents-ch', _('Only Swiss Accents Detailed')),
        )
    BRAILLE_TOC_DEPTH_CHOICES = (
        ('0', 0),
        ('1', 1),
        ('2', 2),
        ('3', 3),
        ('4', 4),
        ('5', 5),
        ('6', 6),
        )
    BRAILLE_FOOTNOTE_PLACEMENT_CHOICES = (
        ('standard', _('Standard')),
        ('end_vol', _('At end of volume')),
        ('level1', _('At end of level1')),
        ('level2', _('At end of level2')),
        ('level3', _('At end of level3')),
        ('level4', _('At end of level4')),
        )
    cells_per_line = forms.IntegerField(label=_("Cells per Line"), initial=28, min_value=1, max_value=255)
    lines_per_page = forms.IntegerField(label=_("Lines per Page"), initial=28, min_value=1, max_value=255)
    contraction = forms.TypedChoiceField(
        label=_("Contraction"), 
        choices=BRAILLE_CONTRACTION_GRADE_CHOICES, 
        initial='2',
        coerce=int)
    hyphenation = forms.BooleanField(
        label=_("Hyphenation"), 
        required=False, initial=False)
    toc_level = forms.TypedChoiceField(
        label=_("Depth of table of contents"), 
        choices=BRAILLE_TOC_DEPTH_CHOICES, 
        coerce=int)
    footer_level = forms.TypedChoiceField(
        label=_("Footer up to level"), 
        choices=BRAILLE_TOC_DEPTH_CHOICES, 
        coerce=int)
    include_macros = forms.BooleanField(
        label=_("Include SBSForm macros"), required=False, initial=True)
    show_original_page_numbers = forms.BooleanField(
        label=_("Show original page numbers"), required=False, initial=True)
    show_v_forms = forms.BooleanField(
        label=_("Show V-Forms"), required=False, initial=True)
    downshift_ordinals = forms.BooleanField(
        label=_("Downshift Ordinals"), required=False, initial=True)
    enable_capitalization = forms.BooleanField(
        label=_("Enable Capitalization"), required=False)
    detailed_accented_characters = forms.ChoiceField(
        label=_("Accented Characters"), 
        choices=BRAILLE_ACCENTS_CHOICES,
        initial='de-accents-ch')
    footnote_placement = forms.ChoiceField(
        label=_("Placement of Footnotes"), 
        choices=BRAILLE_FOOTNOTE_PLACEMENT_CHOICES,
        initial='standard')

class XHTMLForm(forms.Form):
    genToc = forms.BooleanField(
        label=_("Generate a table of contents"), 
#        help_text=_("Generates a Table of Contents"),
        required=False)
    daisyNoterefs = forms.BooleanField(
        label=_("DAISY 2.02 style noterefs"), 
#        help_text=_("Put bodyref attributes on note references (required by Daisy 2.02 skippability recommendation)"),
        required=False)

class RTFForm(forms.Form):
    inclTOC = forms.BooleanField(label=_("Generate a table of contents"), required=False, initial=True)
    inclPagenum = forms.BooleanField(label=_("Show original page numbers"), required=False, initial=True)

class EPUBForm(forms.Form):
    pass

class TextOnlyFilesetForm(forms.Form):
    FILESET_OUTPUTENCODING_CHOICES = (
        ('utf-8', _('utf-8')),
        ('iso-8859-1', _('iso-8859-1')),
        ('Shift_JIS', _('Shift_JIS')),
        )
    outputEncoding = forms.ChoiceField(
        label=_("Output encoding"), choices=FILESET_OUTPUTENCODING_CHOICES)
    doAbbrAcronymDetection = forms.BooleanField(
        label=_("Abbreviation and acronym detection"), required=False, initial=True)
    doSentenceDetection = forms.BooleanField(
        label=_("Sentence detection"), required=False, initial=True)
    doWordDetection = forms.BooleanField(
        label=_("Word detection"), required=False)

class TextOnlyDTBForm(forms.Form):
    ebookNumber = forms.RegexField(label=_("EBook Number"),regex="^EB\d{5}")

class ODTForm(forms.Form):
    MATH_CHOICES = (
        ('ASCIIMATH', _('AsciiMath')),
        ('MATHML', _('MathML')),
        ('BOTH', _('Both')),
        )
    IMAGE_CHOICES = (
        ('DROP', _('None')),
        ('LINK', _('Linked')),
        ('EMBED', _('Embedded')),
        )
    asciimath = forms.ChoiceField(
        label=_("Math"),
#        help_text=_("Select how to render AsciiMath"),
        choices=MATH_CHOICES,
        initial='BOTH')
    phonetics = forms.BooleanField(
        label=_("Phonetics"),
#        help_text=_("Select whether to show Phonetics"),
        required=False, initial=True)
    images = forms.ChoiceField(
        label=_("Images"),
        choices=IMAGE_CHOICES,
        initial='LINK')
    line_numbers = forms.BooleanField(
        label=_("Line Numbers"),
#        help_text=_("Select whether to show line numbers"),
        required=False, initial=True)
    page_numbers = forms.BooleanField(
        label=_("Page Numbers"),
#        help_text=_("Select whether to show page numbers"),
        required=False, initial=True)
    page_numbers_float = forms.BooleanField(
        label=_("Floating Page Numbers"),
#        help_text=_("Select whether page numbers should float to the end of a paragraph"),
        required=False, initial=False)
    answer = forms.CharField(
        label=_("Answer Markup"),
#        help_text=_("Markup for answer fields"),
        initial="_..",
        )

class DTBForm(forms.Form):
    NARRATOR_BITRATE_CHOICES = (
        (32, _('32 kbit/s')),
        (48, _('48 kbit/s')),
        (64, _('64 kbit/s')),
        (128, _('128 kbit/s')),
        )

    bitrate = forms.TypedChoiceField(
        label=_("MP3 Bitrate"), 
#        help_text=_("Select output MP3 encoding bitrate"),
        choices=NARRATOR_BITRATE_CHOICES, 
        coerce=int)
    doSentDetection = forms.BooleanField(
        label=_("Sentence detection"), 
#        help_text=_("Select whether to apply sentence detection"),
        required=False, initial=True)
    multiLang = forms.BooleanField(
        label=_("Multi-language support"), 
#        help_text=_("Select whether to use different TTS voices depending on the xml:lang attributes"),
        required=False, initial=True)
#     dtbookFix = forms.BooleanField(
#         label=_("DTBook Fix"), 
# #        help_text=_("Select whether to apply DTBook Fix routines"),
#         required=False)

class CSVUploadForm(forms.Form):
    csv = forms.FileField(
        label = _("CSV File"), 
        help_text = _("CSV File containing document meta data"))

class SalePDFForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(SalePDFForm, self).__init__(*args, **kwargs) 
        self.fields['font_size'].choices = LargePrintProfile.FONTSIZE_CHOICES[-3:]

    class Meta:
        model = LargePrintProfile
        fields = ('font_size',)
    
class PartialProductForm(forms.Form):
    isbn = forms.CharField()
    productNumber = forms.CharField()
