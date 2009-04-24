from daisyproducer import settings
from django.contrib.auth.models import User, Group
from django.db import models
from django.forms import ModelForm

class StateError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class State(models.Model):
    name = models.CharField(unique=True, max_length=32)
    next_states = models.ManyToManyField("self", symmetrical=False, blank=True)
    responsible = models.ManyToManyField(Group)
    sort_order = models.PositiveSmallIntegerField()

    def __unicode__(self):
        return self.name

    def transitionTo(self, state):
        if not isinstance(state, State):
            raise TypeError("'%s' is not a registered state" % state)
        if not state in self.next_states.all():
            raise StateError("Cannot transition to %s from %s" % (self.name, state.name))
        return state


    class Meta:
        ordering = ['sort_order']

class Document(models.Model):

    title = models.CharField(
        max_length=255, 
        help_text="The title of the DTB, including any subtitles")
    author = models.CharField(
        max_length=255, 
        help_text="Names of primary author or creator of the intellectual content of the publication",
        blank=True)
    subject = models.CharField(
        max_length=255, 
        help_text="The topic of the content of the publication",
        blank=True)
    description = models.TextField(
        help_text="Plain text describing the publication's content",
        blank=True)
    publisher = models.CharField(
        max_length=255,
        default=settings.DAISY_DEFAULT_PUBLISHER,
        help_text="The agency responsible for making the DTB available")
    date = models.DateField(
        auto_now_add=True,
        help_text="Date of publication of the DTB")
    identifier = models.CharField(
        max_length=255, 
        help_text="A string or number identifying the DTB")
    source = models.CharField(
        max_length=10, 
        help_text="A reference to a resource (e.g., a print original, ebook, etc.) from which the DTB is derived. Best practice is to use the ISBN when available", 
        blank=True)
    language_choices = (('de-CH', 'de-CH',),)
    language = models.CharField(
        max_length=10,
        choices=language_choices,
        help_text="Language of the content of the publication")
    rights = models.CharField(
        max_length=255, 
        help_text="Content: Information about rights held in and over the DTB",
        blank=True)
    
    sourceDate = models.DateField(
        "Source Date",
        help_text="Date of publication of the resource (e.g., a print original, ebook, etc.) from which the DTB is derived",
        null=True, blank=True)
    sourceEdition = models.CharField(
        "Source Edition", 
        max_length=255, 
        help_text="A string describing the edition of the resource (e.g., a print original, ebook, etc.) from which the DTB is derived",
        blank=True)
    sourcePublisher = models.CharField(
        "Source Publisher", 
        max_length=255, 
        help_text="The agency responsible for making available the resource (e.g., a print original, ebook, etc.) from which the DTB is derived",
        blank=True)
    sourceRights = models.CharField(
        "Source Rights", 
        max_length=255, 
        help_text="Information about rights held in and over the resource (e.g., a print original, ebook, etc.) from which the DTB is derived",
        blank=True)

    state = models.ForeignKey(State)
    assigned_to = models.ForeignKey(User, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title

    def latest_version(self):
        return self.version_set.latest()

    def transitionTo(self, state):
        self.assigned_to = None
        self.state = self.state.transitionTo(state)
        self.save()

    def save(self):
        # set initial state
        if not self.pk:
            self.state = State.objects.filter(name='new')[0]
        super(Document, self).save()

def get_version_path(instance, filename):
        return '%s/versions/%s.xml' % (instance.document_id, instance.id)
    
class Version(models.Model):
    comment = models.CharField(max_length=255)
    document = models.ForeignKey(Document)
    content = models.FileField(upload_to=get_version_path)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        get_latest_by = "created_at"
        ordering = ['-created_at']

def get_attachment_path(instance, filename):
        return '%s/attachments/%s' % (instance.document_id, filename)

class Attachment(models.Model):

    MIME_TYPE_CHOICES = (
        ('application/pdf', 'Portable Document Format, PDF'),
        ('application/msword', 'Microsoft Word files'),
        ('application/rtf', 'Microsoft RTF files'),
        ('text/html', 'HTML'),
        )
    
    comment = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=32, choices=MIME_TYPE_CHOICES)
    document = models.ForeignKey(Document)
    content = models.FileField(upload_to=get_attachment_path)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

# Profiles
class BrailleProfile(models.Model):

    BRAILLE_CONTRACTION_GRADE_CHOICES = (
        ('0', 'Grade 0'),
        ('1', 'Grade 1'),
        ('2', 'Grade 2'),
        )

    cellsPerLine = models.PositiveSmallIntegerField("Cells per Line", default=40, max_length=4)
    linesPerPage = models.PositiveSmallIntegerField("Line per Page", default=28, max_length=4)
    contraction = models.PositiveSmallIntegerField(default=0, choices=BRAILLE_CONTRACTION_GRADE_CHOICES)
    hyphenation = models.BooleanField(default=True)
    showOriginalPageNumbers = models.BooleanField("Show original page numbers", default=True)
    enableCapitalization = models.BooleanField("Enable Capitalization")
    detailedAccentedCharacters = models.BooleanField("Detailed Accented Characters")

class BrailleProfileForm(ModelForm):
    class Meta:
        model = BrailleProfile

class LargePrintProfile(models.Model):
    FONTSIZE_CHOICES = (
        ('12pt', '12pt'),
        ('14pt', '14pt'),
        ('17pt', '17pt'),
        ('20pt', '20pt'),
        )
    
    FONT_CHOICES = (
        ('Tiresias LPfont', 'Tiresias LPfont'),
        ('LMRoman10 Regular', 'LMRoman10 Regular'),
        ('LMSans10 Regular', 'LMSans10 Regular'),
        ('LMTypewriter10 Regular', 'LMTypewriter10 Regular'),
        )
    
    PAGESTYLE_CHOICES = (
        ('plain', 'Plain'),
        ('withPageNums', 'With original page numbers'),
        ('scientific', 'Scientific'),
        )
    
    ALIGNMENT_CHOICES = (
        ('justified', 'justified'),
        ('left', 'left aligned'),
        )
    
    PAPERSIZE_CHOICES = (
        ('a3paper', 'a3paper'),
        ('a4paper', 'a4paper'),
        )
    
    fontSize = models.CharField("Fontsize", default='17pt', max_length=4, choices=FONTSIZE_CHOICES)
    font = models.CharField(default='Tiresias LPfont', max_length=60, choices=FONT_CHOICES)
    pageStyle = models.CharField("Page style", default='plain', max_length=16, choices=PAGESTYLE_CHOICES)
    alignment = models.CharField(default='justified', max_length=16, choices=ALIGNMENT_CHOICES)
    paperSize = models.CharField("Papersize", default='a4paper', max_length=16, choices=PAPERSIZE_CHOICES)

class LargePrintProfileForm(ModelForm):
    class Meta:
        model = LargePrintProfile

