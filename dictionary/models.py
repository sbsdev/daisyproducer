# coding=utf-8
import datetime

from daisyproducer.documents.models import Document
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

class Word(models.Model):

    MAX_WORD_LENGTH = 100
    WORD_TYPE_CHOICES = (
    # (0) keine Einschränkung: die angezeigte Übersetzung dieses Wortes ist die EINZIG MÖGLICHE
    # und dieses Wort kann kein Name sein (Wort wird zukünftig in .xml-Datei NIE mit brl:name
    # ausgezeichnet): z.B. Tisch, Stuhl, Automatik
        (0, _('None')),
    # (1) auch als Name: die angezeigte Übersetzung dieses Wortes ist die EINZIG MÖGLICHE und
    # dieses Wort muss ein Name sein (Wort darf zukünftig in .xml-Datei mit brl:name
    # ausgezeichnet werden, muss aber nicht, weil gleiche Übersetzung): z.B. Hug, Meier,
    # Müller, Hoffmann, Ackermann
        (1, _('Also as a name')),
    # (2) Name: die angezeigte Übersetzung dieses Wortes gilt nur als Namen. Daneben existiert
    # ein entsprechender Nicht-Name, welcher anders übersetzt wird (Wort wird zukünftig in
    # .xml-Datei mit oder ohne brl:name ausgezeichnet, je nach gewünschter Übersetzung): z.B.
    # Kaufmann, Waldmann, Beat
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
