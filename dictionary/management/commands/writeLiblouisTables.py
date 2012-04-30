from daisyproducer.dictionary.brailleTables import writeWhiteListTables, writeLocalTables
from daisyproducer.dictionary.models import Word
from daisyproducer.documents.models import Document
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    args = ''
    help = 'Write Liblouis tables from the confirmed words in the dictionary'

    def handle(self, *args, **options):
        # write new global white lists
        verbosity = int(options['verbosity'])
        if verbosity >= 2:
            self.stderr.write('Writing new global white lists...\n')
        writeWhiteListTables(Word.objects.filter(isConfirmed=True).filter(isLocal=False).order_by('untranslated'))
        # update local tables
        if verbosity >= 2:
            self.stderr.write('Updating local tables...\n')
        writeLocalTables(Document.objects.all())
