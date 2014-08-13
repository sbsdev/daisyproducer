from django.db import models
from fractions import Fraction
from django.core.validators import MaxValueValidator,MinValueValidator
from daisyproducer.documents.models import Document

class DocumentStatistic(models.Model):
    """Keep a record of how many words in a document are unknown"""

    # The date
    date = models.DateTimeField(auto_now_add=True)

    # Reference to the document
    document = models.ForeignKey(Document)

    # Contraction grade
    grade = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(2)])

    # The total number of words in the document
    total = models.PositiveIntegerField()

    # The number of unknown words in the document
    unknown = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        self.clean_fields()
        super(DocumentStatistic, self).save(*args, **kwargs)
