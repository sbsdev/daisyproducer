# coding=utf-8
import codecs
from daisyproducer.dictionary.importExport import exportWords
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

class Command(BaseCommand):
    help = 'Dump the global dictionary to a file'
    
    @transaction.commit_on_success
    def add_arguments(self, parser):
        parser.add_argument(
            'dictionary_file',
            nargs=1,
            help = 'Dump the global dictionary to a given file'
        )

    def handle(self, *args, **options):
        file_name = options['dictionary_file'][0]

        try:
            f = codecs.open(file_name, "w", "utf-8")
        except IndexError:
            raise CommandError('No file specified')
        exportWords(f)
        f.close()
        verbosity = int(options['verbosity'])
        if verbosity >= 1:
            self.log("Words written to %s\n" % file_name)
        
    def log(self, message):
        self.stdout.write("%s\n" % message)
