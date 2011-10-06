from daisyproducer.documents.models import Document
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Word(models.Model):

    WORD_TYPE_CHOICES = (
        ('0', _('No restriction')),
        ('1', _('Also as a name')),
        ('2', _('Only as a name')),
        ('3', _('Also as a place')),
        ('4', _('Only as a place')),
        ('5', _('Homograph default')),
        ('6', _('Homograph alternative')),
        ('7', _('Dialect')),
        )

    untranslated = models.CharField(max_length=255)
    grade1 = models.CharField(max_length=255)
    grade2 = models.CharField(max_length=255)
    document = models.ManyToManyField(Document, null=True, blank=True)
    type = models.PositiveSmallIntegerField(_("Type"), default=0, choices=WORD_TYPE_CHOICES)
    isConfirmed = models.BooleanField()

    def __unicode__(self):
        return self.untranslated

