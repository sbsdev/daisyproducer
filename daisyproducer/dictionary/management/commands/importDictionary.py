# coding=utf-8
import codecs
from daisyproducer.dictionary.importExport import WordReader, validateBraille
from daisyproducer.dictionary.models import GlobalWord
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from django.db import transaction

class Command(BaseCommand):
    help = 'Import the given file as a dictionary'
    output_transaction = True

    def add_arguments(self, parser):
        parser.add_argument(
            'dictionary_file',
            nargs=1,
            help = 'Import the given file as a dictionary'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        file_name = options['dictionary_file'][0]
        try:
            f = codecs.open(file_name, "r", "utf-8" )
        except IndexError:
            raise CommandError('No dictionary file specified')
        except IOError:
            raise CommandError('Dictionary file "%s" not found' % file_name)

        verbosity = int(options['verbosity'])

        self.numberOfImports = 0
        self.numberOfErrors = 0

        reader = WordReader(f)
        while True:
            try:
                word = reader.next()
                if '#' in word['untranslated']:
                    # ignore rows where the untranslated word has some # in it. These lines need to be fixed
                    raise Exception("Invalid characters ('#') in untranslated: %s" % word['untranslated'])
                validateBraille(word['braille'])
                try:
                    GlobalWord(**word).save()
                except IntegrityError:
                    raise Exception('Duplicate word "%s"' % word)
                self.numberOfImports += 1
            except StopIteration:
                break
            except Exception as e:
                self.error(e, reader.currentLine())

        f.close()
        if verbosity >= 1:
            self.log("\n%s words were successfully updated" % self.numberOfImports)
            if self.numberOfErrors > 0:
                self.log("%s errors" % self.numberOfErrors)

    def log(self, message):
        self.stdout.write("%s\n" % message)

    def error(self, message, lineNo=0):
        self.numberOfErrors += 1
        self.log(color.ERROR + "[ERROR] (line %d) %s" % (lineNo, message) + color.END)

class color:
    INSERTED = '\033[1m\033[94m'
    WARNING = '\033[1m\033[93m'
    ERROR = '\033[1m\033[91m'
    DELETED = '\033[1m\033[91m'
    END = '\033[0m\033[0m'

