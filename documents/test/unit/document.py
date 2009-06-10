from django.test import TestCase
from daisyproducer.documents.models import Document

class DocumentTestCase(TestCase):

    def testUnicode(self):
        d = Document(title='foo', publisher='bar', identifier='baz')
        self.assertEquals(d.__unicode__(), 'foo')

