from django.db import models
from django.forms import ModelForm

from daisyproducer.documents.stateMachine import Machine

STATES = (
    'new',
    'scanned',
    'ocred',
    'marked-up',
    'corrected',
    'production-ready',
    )

STATE_CHOICES = tuple([(state, state) for state in STATES])

class Document(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    state = models.CharField(max_length=32, default='new', choices=STATE_CHOICES)
    content = models.FileField(upload_to='media')

    def __init__(self, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)

        states = tuple([t[0] for t in STATE_CHOICES])

        self.machine = Machine(self, states, initial='new')

        self.machine.event('scan', {'from': 'new', 'to': 'scanned'})
        self.machine.event('ocr', {'from': 'scanned', 'to': 'ocred'})
        self.machine.event('markup', {'from': 'ocred', 'to': 'marked-up'})
        self.machine.event('correct', {'from': 'marked-up', 'to': 'corrected'})
        self.machine.event('ready', {'from': 'corrected', 'to': 'production-ready'})

    def __unicode__(self):
        return self.title

class DocumentForm(ModelForm):
    class Meta:
        model = Document


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

