from daisyproducer.dictionary.brailleTables import writeWhiteListTables, writeLocalTables
from daisyproducer.dictionary.models import GlobalWord
from daisyproducer.documents.models import Document
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    args = ''
    help = 'Write Liblouis tables from the confirmed words in the dictionary'

    def handle(self, *args, **options):
        # write new global white lists
        writeWhiteListTables(GlobalWord.objects.filter(isLocal=False).order_by('untranslated'))
        # update local tables
        writeLocalTables(Document.objects.all())
