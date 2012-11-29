import shutil, tempfile, os, csv
from optparse import make_option

from daisyproducer.documents.models import Document
from django.core.management.base import BaseCommand
from django.utils.encoding import smart_str

class Command(BaseCommand):
    args = ''
    help = 'Clean out old versions from the database and the file system'

    option_list = BaseCommand.option_list + (
        make_option(
            '--numberOfVersionsKept',
            type="int",
            dest='numberOfVersionsKept',
            default=7,
            help='Number of versions that should be kept for a document. If a document contains more versions than the specified number only said number of versions are kept. Older versions are removed.'),
        )

    def handle(self, *args, **options):
        numberOfVersionsKept = options['numberOfVersionsKept']
        verbosity = int(options['verbosity'])

        for document in Document.objects.all():
            if verbosity >= 2:
                self.stdout.write('Removing excess versions for %s...\n' % smart_str(document.title))
            document.remove_excess_versions(numberOfVersionsKept)
