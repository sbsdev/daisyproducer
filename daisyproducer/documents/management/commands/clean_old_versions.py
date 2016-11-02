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
            default=3,
            help='Number of versions that should be kept for a document. If a document contains more versions than the specified number only said number of versions are kept. Older versions are removed.'),
        )

    def handle(self, *args, **options):
        numberOfVersionsKept = options['numberOfVersionsKept']
        verbosity = int(options['verbosity'])
        removed = 0

        for document in Document.objects.all():
            if verbosity >= 1:
                self.stdout.write('Removing excess versions for %s [%s]...\n' % (smart_str(document.title), document.id))

            versions = document.version_set.all()
            versions_to_remove = versions[numberOfVersionsKept:]

            if verbosity >= 2:
                self.stdout.write('Number of versions: %s\n' % len(versions))
            
            for version in versions_to_remove:
                if verbosity >= 2:
                    self.stdout.write('Removing version for "%s"...\n' % smart_str(version))
                version.delete()
                removed += 1

        if verbosity >= 1:
            self.stdout.write('Removed %s excess versions\n' % removed)
