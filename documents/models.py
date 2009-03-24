from django.db import models
from django.forms import ModelForm

class Document(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    content = models.FileField(upload_to='media')


class DocumentForm(ModelForm):
    class Meta:
        model = Document


BRAILLE_CONTRACTION_GRADE_CHOICES = (
    ('0', 'Grade 0'),
    ('1', 'Grade 1'),
    ('2', 'Grade 2'),
)

class BrailleProfile(models.Model):
    cellsPerLine = models.PositiveSmallIntegerField(default=40)
    linesPerPage = models.PositiveSmallIntegerField(default=28)
    contraction = models.PositiveSmallIntegerField(default=0, choices=BRAILLE_CONTRACTION_GRADE_CHOICES)
    hyphenation = models.BooleanField(default=True)
    showOriginalPageNumbers = models.BooleanField(default=True)
    enableCapitalization = models.BooleanField()
    detailedAccentedCharacters = models.BooleanField()

class BrailleProfileForm(ModelForm):
    class Meta:
        model = BrailleProfile

