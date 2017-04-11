# coding=utf-8
import codecs
from daisyproducer.dictionary.importExport import WordReader, columnize
from daisyproducer.dictionary.models import GlobalWord
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_unicode
from django.db import transaction

inverseTypeMap = { 0: '*', 1: 'n', 2: 'N', 3: 'p', 4: 'P', 5: 'H' }

class Command(BaseCommand):
    help = 'Delete words in the given file from the global dictionary (file must be encoded in UTF-8)'

    def add_arguments(self, parser):
        parser.add_argument(
            'dictionary_file',
            nargs=1,
            help = 'File containing the words to be deleted from the global dictionary (must be encoded in UTF-8)'
        )

        parser.add_argument(
            '--dry-run',
            default=False,
            help='Do a simulation before actually performing the action'
        )

        parser.add_argument(
            '--force',
            default=False,
            help='Ignore any warnings and just delete the words'
        )

    @transaction.commit_on_success
    def handle(self, *args, **options):
        file_name = options['dictionary_file'][0]
        try:
            f = open(file_name)
        except IndexError:
            raise CommandError('No dictionary file specified')
        except IOError:
            raise CommandError('Dictionary file "%s" not found' % file_name)

        self.logger = codecs.getwriter(self.stdout.encoding if self.stdout.isatty() else 'utf-8')(self.stdout)

        verbosity = int(options['verbosity'])
        dry_run = options['dry_run']
        force = options['force']

        if not dry_run and not force:
            self.log("Warning: this action cannot be undone. Specify the --dry-run option to do a simulation first.")
            raw_input("Hit Enter to continue, or Ctrl-C to abort.")

        self.numberOfDeletes = 0
        self.numberOfErrors = 0

        if dry_run:
            verbosity = 2
        if verbosity >= 1:
            self.log("Deleting global words...")
            self.log("==================================================================================================================")
            self.log(columnize(("type", "grade", "untranslated", "braille"), (5,5,50,50)))
            self.log("==================================================================================================================")

        reader = WordReader(f)
        while True:
            try:
                deletion = reader.next()
                word = None
                try:
                    word = GlobalWord.objects.get(
                                untranslated=deletion['untranslated'],
                                braille=deletion['braille'],
                                grade=deletion['grade'],
                                type=deletion['type'],
                                homograph_disambiguation=deletion['homograph_disambiguation'])
                except ObjectDoesNotExist:
                    raise Exception("Word could not be found in the global dictionary: %s" % deletion)
                if verbosity >= 1:
                    self.log(columnize((inverseTypeMap[word.type],
                                        str(word.grade),
                                        word.untranslated,
                                        word.braille),
                                       (5,5,50,50)))
                if not dry_run:
                    word.delete()
                self.numberOfDeletes += 1
            except StopIteration:
                break
            except Exception as e:
                self.log(self.error(e, reader.currentLine()))

        f.close()
        if verbosity >= 1:
            self.log("==================================================================================================================")
            self.log("%s words were deleted" % self.numberOfDeletes)
            if self.numberOfErrors > 0:
                self.log("%s errors" % self.numberOfErrors)

    def log(self, message):
        self.logger.write(u"%s\n" % smart_unicode(message))

    def error(self, message, lineNo=0):
        self.numberOfErrors += 1
        if lineNo > 0:
            message = "(line %d) %s" % (lineNo, message)
        return color.ERROR + "[ERROR] %s" % (message) + color.END

class color:
    ERROR = r'[01;31m'
    END = r'[0m'
