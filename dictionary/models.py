import datetime

from daisyproducer.documents.models import Document
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Word(models.Model):

    MAX_WORD_LENGTH = 100
    WORD_TYPE_CHOICES = (
        (0, _('None')),
        (1, _('Also as a name')),
        (2, _('Name')),
        (3, _('Also as a place')),
        (4, _('Place')),
        (5, _('Homograph')),
        )

    untranslated = models.CharField(_("Untranslated"), max_length=MAX_WORD_LENGTH, db_index=True)
    braille = models.CharField(_("Braille"), max_length=MAX_WORD_LENGTH)
    grade = models.PositiveSmallIntegerField(_("Grade"), db_index=True)
    type = models.PositiveSmallIntegerField(_("Markup"), default=0, choices=WORD_TYPE_CHOICES, db_index=True)
    homograph_disambiguation = models.CharField(_("Homograph Disambiguation"), max_length=MAX_WORD_LENGTH, blank=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.untranslated

class GlobalWord(Word):

    class Meta:
        unique_together = ("untranslated", "type", "grade", "homograph_disambiguation")

class LocalWord(Word):
    isLocal = models.BooleanField(_("Local"), default=False)
    isConfirmed = models.BooleanField(_("Confirmed"), default=False)
    document = models.ForeignKey(Document)

    class Meta:
        unique_together = ("untranslated", "type", "grade", "homograph_disambiguation", "document")
