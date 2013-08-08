# coding=utf-8
import codecs
from daisyproducer.dictionary.importExport import WordReader, columnize
from daisyproducer.dictionary.models import GlobalWord
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import smart_unicode
from django.db import transaction
from optparse import make_option

inverseTypeMap = { 0: '*', 1: 'n', 2: 'N', 3: 'p', 4: 'P', 5: 'H' }

class Command(BaseCommand):
    args = 'dictionary_file'
    help = 'Delete words in the given file from the global dictionary (file must be encoded in UTF-8)'

    option_list = BaseCommand.option_list + (
        make_option(
            '--dry-run',
            default=False,
            help='Do a simulation before actually performing the action'),)

    @transaction.commit_on_success
    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Incorrect number of arguments')
        try:
            f = open(args[0])
        except IndexError:
            raise CommandError('No dictionary file specified')
        except IOError:
            raise CommandError('Dictionary file "%s" not found' % args[0])

        verbosity = int(options['verbosity'])
        dry_run = options['dry_run']
        if not dry_run:
            self.log("Warning: this action cannot be undone. Specify the --dry-run option to do a simulation first.")
            raw_input("Hit Enter to continue, or Ctrl-C to abort.")

        self.logger = codecs.getwriter(self.stdout.encoding)(self.stdout)

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
