from django.db import models
from django.forms import ModelForm
from daisyproducer.documents.stateMachine import Machine

class Document(models.Model):

    STATES = (
        'new',
        'scanned',
        'ocred',
        'marked_up',
        'proof_read',
        'approved',
        )
    
    TRANSITIONS = (
        'scanning',
        'ocr', 
        'marking_up', 
        'proof_reading', 
        'approving',
        None,
        )
    
    TRANSITION_STATE_MAP = dict(zip(TRANSITIONS,STATES)) # which transition leads to which state
    STATE_TRANSITION_MAP = dict(zip(STATES,TRANSITIONS)) # which state is coming from which transition

    STATE_CHOICES = tuple([(state, state) for state in STATES])

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    state = models.CharField(max_length=32, default='new', choices=STATE_CHOICES)

    def __init__(self, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)

        states = Document.STATES

        self.machine = Machine(self, states, initial='new')

        self.machine.event('scanning', {'from': 'new', 'to': 'scanned'})
        self.machine.event('ocring', {'from': 'scanned', 'to': 'ocred'})
        self.machine.event('marking-up', {'from': 'ocred', 'to': 'marked_up'})
        self.machine.event('proof-reading', {'from': 'marked_up', 'to': 'proof_read'})
        self.machine.event('approving', {'from': 'proof_read', 'to': 'approved'})
        self.machine.event('fixing-errata', {'from': 'approved', 'to': 'marked_up'})
        self.machine.event('fixing-typos', {'from': 'proof_read', 'to': 'marked_up'})

    def __unicode__(self):
        return self.title

    def latest_version(self):
        return self.version_set.latest()

class Version(models.Model):
    content = models.FileField(upload_to='media')
    document = models.ForeignKey(Document)
    version_date = models.DateField()

    class Meta:
        get_latest_by = "version_date"

MIME_TYPE_CHOICES = (
    ('application/pdf', 'Portable Document Format, PDF'),
    ('application/msword', 'Microsoft Word files'),
    ('application/rtf', 'Microsoft RTF files'),
    ('text/html', 'HTML'),
)

class Attachment(models.Model):
    comment = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=32, choices=MIME_TYPE_CHOICES)
    content = models.FileField(upload_to='media')
    document = models.ForeignKey(Document)
    
# Profiles
BRAILLE_CONTRACTION_GRADE_CHOICES = (
    ('0', 'Grade 0'),
    ('1', 'Grade 1'),
    ('2', 'Grade 2'),
)

class BrailleProfile(models.Model):
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

class LargePrintProfile(models.Model):
    fontSize = models.CharField("Fontsize", default='17pt', max_length=4, choices=FONTSIZE_CHOICES)
    font = models.CharField(default='Tiresias LPfont', max_length=60, choices=FONT_CHOICES)
    pageStyle = models.CharField("Page style", default='plain', max_length=16, choices=PAGESTYLE_CHOICES)
    alignment = models.CharField(default='justified', max_length=16, choices=ALIGNMENT_CHOICES)
    paperSize = models.CharField("Papersize", default='a4paper', max_length=16, choices=PAPERSIZE_CHOICES)

class LargePrintProfileForm(ModelForm):
    class Meta:
        model = LargePrintProfile

