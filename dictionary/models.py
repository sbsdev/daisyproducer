import datetime

from daisyproducer.documents.models import Document
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Word(models.Model):

    WORD_TYPE_CHOICES = (
        (0, _('No restriction')),
        (1, _('Also as a name')),
        (2, _('Name')),
        (3, _('Also as a place')),
        (4, _('Place')),
        (5, _('Homograph')),
        )

    untranslated = models.CharField(_("Untranslated"), max_length=255, db_index=True)
    grade1 = models.CharField(_("Grade1"), max_length=255)
    grade2 = models.CharField(_("Grade2"), max_length=255)
    documents = models.ManyToManyField(Document, null=True, blank=True)
    type = models.PositiveSmallIntegerField(_("Type"), default=0, choices=WORD_TYPE_CHOICES)
    homograph_disambiguation = models.CharField(_("Homograph Disambiguation"), max_length=255, blank=True)
    isConfirmed = models.BooleanField(_("Confirmed"), default=False)
    isLocal = models.BooleanField(_("Local"), default=False)
    use_for_word_splitting = models.BooleanField(_("Use for word splitting"), default=True)
    created_at = models.DateTimeField(_("Created"))
    modified_at = models.DateTimeField(_("Last Modified"))
    modified_by = models.ForeignKey(User, verbose_name=_("Modified by"))

    class Meta:
        unique_together = ("untranslated", "type", "isConfirmed", "homograph_disambiguation")

    def __unicode__(self):
        return self.untranslated

    def save(self):
        if not self.id:
            self.created_at = datetime.datetime.now()
        self.modified_at = datetime.datetime.now()
        super(Word, self).save()
