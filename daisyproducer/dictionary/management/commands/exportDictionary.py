# coding=utf-8
import codecs
from daisyproducer.dictionary.importExport import exportWords
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

class Command(BaseCommand):
    args = 'dictionary_file'
    help = 'Dump the global dictionary to a file'
    
    @transaction.commit_on_success
    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Incorrect number of arguments')
        try:
            f = codecs.open(args[0], "w", "utf-8")
        except IndexError:
            raise CommandError('No file specified')
        exportWords(f)
        f.close()
        verbosity = int(options['verbosity'])
        if verbosity >= 1:
            self.log("Words written to %s\n" % args[0])
        
    def log(self, message):
        self.stdout.write("%s\n" % message)