import uuid, datetime
from os.path import join
from shutil import rmtree

from daisyproducer.documents.storage import OverwriteStorage
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db import models
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

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
    
    # used for admin view
    def all_next_states(self):
        return ",".join([state.name for state in self.next_states.all()])

    # used for admin view
    def all_responsible(self):
        return ",".join([group.name for group in self.responsible.all()])

    class Meta:
        ordering = ['sort_order']

class Document(models.Model):

    # see http://www.daisy.org/z3986/2005/Z3986-2005.html for a description of all the metadata fields
    title = models.CharField(
        _("Title"),
        max_length=255, 
        help_text=_("The title of the DTB, including any subtitles"))
    author = models.CharField(
        _("Author"),
        max_length=255, 
        help_text=_("Names of primary author or creator of the intellectual content of the publication"),
        blank=True)
    subject = models.CharField(
        _("Subject"),
        max_length=255, 
        help_text=_("The topic of the content of the publication"),
        blank=True)
    description = models.TextField(
        _("Description"),
        help_text=_("Plain text describing the publication's content"),
        blank=True)
    publisher = models.CharField(
        _("Publisher"),
        max_length=255,
        default=settings.DAISY_DEFAULT_PUBLISHER,
        help_text=_("The agency responsible for making the DTB available"))
    date = models.DateField(
        _("Date"),
        help_text=_("Date of publication of the DTB"))
    identifier = models.CharField(
        _("Identifier"),
        max_length=255,
        unique=True,
        help_text=_("A string or number identifying the DTB"))
    source = models.CharField(
        _("Source"),
        max_length=20, 
        help_text=_("A reference to a resource (e.g., a print original, ebook, etc.) from which the DTB is derived. Best practice is to use the ISBN when available"), 
        blank=True)
    language_choices = (('de', 'de'),
                        ('de-1901', 'de-1901',),
                        # ('de-CH', 'de-CH',),
                        # ('de-CH-1901', 'de-CH-1901',),
                        # ('gsw', 'gsw',),
                        ('en', 'en',),
                        ('fr', 'fr',),
                        # ('it', 'it',),
                        ('es', 'es',),
                        # ('und', 'Undefined',),
                        )
    language = models.CharField(
        _("Language"),
        max_length=10,
        choices=language_choices,
        help_text=_("Language of the content of the publication"))
    rights = models.CharField(
        _("Rights"),
        max_length=255, 
        help_text=_("Information about rights held in and over the DTB"),
        blank=True)
    
    source_date = models.DateField(
        _("Source Date"),
        help_text=_("Date of publication of the resource (e.g., a print original, ebook, etc.) from which the DTB is derived"),
        null=True, blank=True)
    source_edition = models.CharField(
        _("Source Edition"), 
        max_length=255, 
        help_text=_("A string describing the edition of the resource (e.g., a print original, ebook, etc.) from which the DTB is derived"),
        blank=True)
    source_publisher = models.CharField(
        _("Source Publisher"), 
        max_length=255, 
        help_text=_("The agency responsible for making available the resource (e.g., a print original, ebook, etc.) from which the DTB is derived"),
        blank=True)
    source_rights = models.CharField(
        _("Source Rights"), 
        max_length=255, 
        help_text=_("Information about rights held in and over the resource (e.g., a print original, ebook, etc.) from which the DTB is derived"),
        blank=True)

    PRODUCTION_SERIES_CHOICES = (
        ('SJW', 'SJW'),
        ('PPP', 'Rucksack-Buch',),
        )
    production_series = models.CharField(
        _("Production Series"), 
        max_length=25, 
        choices=PRODUCTION_SERIES_CHOICES,
        help_text=_("Information about the series under which the book is produced"),
        blank=True)
        
    production_series_number = models.CharField(
        _("Production Series Number"), 
        max_length=25, 
        help_text=_("Information about the number in the series under which the book is produced"),
        blank=True)

    PRODUCTION_SOURCE_CHOICES = (
        ('electronicData', 'Electronic Data'),
        )
    production_source = models.CharField(
        _("Production Source"), 
        max_length=25, 
        choices=PRODUCTION_SOURCE_CHOICES,
        help_text=_("Information about the source from which the book was produced, e.g. scanned book, electronic data, etc"),
        blank=True)
        
    state = models.ForeignKey(State, verbose_name=_("State"))
    assigned_to = models.ForeignKey(User, verbose_name=_("Assigned to"), null=True, blank=True)
    created_at = models.DateTimeField(_("Created"))
    modified_at = models.DateTimeField(_("Last Modified"))

    def __unicode__(self):
        return self.title

    def latest_version(self):
        return self.version_set.latest()

    def transitionTo(self, state):
        self.assigned_to = None
        self.state = self.state.transitionTo(state)
        self.save()

    def has_local_words(self):
        return self.localword_set.exists()

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = datetime.datetime.now()
            self.date = datetime.date.today() 
        self.modified_at = datetime.datetime.now()             
        # set initial state
        if not self.pk and not hasattr(self, 'state'):
            self.state = State.objects.filter(name='new')[0]
        if not self.identifier:
            self.identifier = "ch-sbs-%s" % str(uuid.uuid4())
        super(Document, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        old_id = self.id
        super(Document, self).delete(*args, **kwargs)
        # remove the folders for versions and attachments on the file system
        rmtree(join(settings.MEDIA_ROOT, str(old_id)))

def get_version_path(instance, filename):
        return '%s/versions/%s.xml' % (instance.document_id, instance.id)
    
class Version(models.Model):
    comment = models.CharField(max_length=255)
    document = models.ForeignKey(Document)
    content = models.FileField(upload_to=get_version_path)
    created_by = models.ForeignKey(User, verbose_name=_("Created by"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s, %s, %s' % (self.comment, self.created_by, self.created_at)

    def delete(self, *args, **kwargs):
        # remove the files on the file system
        self.content.delete()
        super(Version, self).delete(*args, **kwargs)
        
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
    created_by = models.ForeignKey(User, verbose_name=_("Created by"))
    created_at = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        # remove the files on the file system
        self.content.delete()
        super(Attachment, self).delete(*args, **kwargs)
        
    class Meta:
        ordering = ['-created_at']

def get_image_path(instance, filename):
    return '%s/images/%s' % (instance.document_id, filename)

class Image(models.Model):

    MIME_TYPE_CHOICES = (
        ('image/jpeg', 'JPEG image'),
        )

    document = models.ForeignKey(Document)
    content = models.FileField(upload_to=get_image_path, storage=OverwriteStorage())

    def __unicode__(self):
        return u'%s, %s' % (self.document, self.content)

    def delete(self, *args, **kwargs):
        # remove the files on the file system
        self.content.delete()
        super(Image, self).delete(*args, **kwargs)

    class Meta:
        unique_together = ('document', 'content')
        ordering = ['content']

class Product(models.Model):
    PRODUCT_TYPE_CHOICES = (
        (0, 'Braille'),
        (1, 'Large Print'),
        (2, 'EBook'),
        (3, 'E-Text'),
        )
    
    identifier = models.CharField(_("Identifier"), max_length=255, unique=True)
    type = models.PositiveSmallIntegerField(_("Type"), choices=PRODUCT_TYPE_CHOICES)
    document = models.ForeignKey(Document)

    def __unicode__(self):
        return self.identifier

# Profiles
class BrailleProfile(models.Model):

    BRAILLE_CONTRACTION_GRADE_CHOICES = (
        ('0', _('Grade 0')),
        ('1', _('Grade 1')),
        ('2', _('Grade 2')),
        )

    cells_per_line = models.PositiveSmallIntegerField(_("Cells per Line"), default=40, max_length=4)
    lines_per_page = models.PositiveSmallIntegerField(_("Lines per Page"), default=28, max_length=4)
    contraction = models.PositiveSmallIntegerField(_("Contraction"), default=0, choices=BRAILLE_CONTRACTION_GRADE_CHOICES)
    hyphenation = models.BooleanField(_("Hyphenation"), default=True)
    show_original_page_numbers = models.BooleanField(_("Show original page numbers"), default=True)
    enable_capitalization = models.BooleanField(_("Enable Capitalization"))
    detailed_accented_characters = models.BooleanField(_("Detailed Accented Characters"))

class BrailleProfileForm(ModelForm):
    class Meta:
        model = BrailleProfile

class LargePrintProfile(models.Model):
    FONTSIZE_CHOICES = (
        ('12pt', '12pt'),
        ('14pt', '14pt'),
        ('17pt', '17pt'),
        ('20pt', '20pt'),
        ('25pt', '25pt'),
        )
    
    FONT_CHOICES = (
        ('Tiresias LPfont', 'Tiresias LPfont'),
        ('LMRoman10 Regular', 'LMRoman10 Regular'),
        ('LMSans10 Regular', 'LMSans10 Regular'),
        ('LMTypewriter10 Regular', 'LMTypewriter10 Regular'),
        )
    
    PAGESTYLE_CHOICES = (
        ('plain', _('Plain')),
        ('withPageNums', _('With original page numbers')),
        ('scientific', _('Scientific')),
        )
    
    ALIGNMENT_CHOICES = (
        ('justified', _('justified')),
        ('left', _('left aligned')),
        )
    
    PAPERSIZE_CHOICES = (
        ('a3paper', 'a3paper'),
        ('a4paper', 'a4paper'),
        )
    
    LINESPACING_CHOICES = (
        ('singlespacing', _('Single spacing')),
        ('onehalfspacing', _('One-and-a-half spacing')),
        ('doublespacing', _('Double spacing')),
        )
    
    ENDNOTE_CHOICES = (
        ('none', _('Plain Footnotes')),
        ('document', _('Document Endnotes')),
        ('chapter', _('Chapter Endnotes')),
        )
    
    font_size = models.CharField(_("Fontsize"), default='17pt', max_length=4, choices=FONTSIZE_CHOICES)
    font = models.CharField(_("Font"), default='Tiresias LPfont', max_length=60, choices=FONT_CHOICES)
    page_style = models.CharField(_("Page style"), default='plain', max_length=16, choices=PAGESTYLE_CHOICES)
    alignment = models.CharField(default='left', max_length=16, choices=ALIGNMENT_CHOICES)
    stock_size = models.CharField(_("Stocksize"), default='a4paper', max_length=16, choices=PAPERSIZE_CHOICES)
    line_spacing = models.CharField(_("Line Spacing"), default='onehalfspacing', max_length=16, choices=LINESPACING_CHOICES)
    replace_em_with_quote = models.BooleanField(_("Replace italics with quote"), default=True)
    end_notes = models.CharField(_("End Notes"), default='none', max_length=16, choices=ENDNOTE_CHOICES)

class LargePrintProfileForm(ModelForm):
    class Meta:
        model = LargePrintProfile

