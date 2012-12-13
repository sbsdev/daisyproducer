# coding=utf-8
import codecs
from daisyproducer.dictionary.importExport import readWord, makeWord, validateBraille

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from django.db import transaction

class Command(BaseCommand):
    args = 'dictionary_file'
    help = 'Import the given file as a dictionary'
    output_transaction = True

    @transaction.commit_on_success
    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Incorrect number of arguments')
        try:
            f = codecs.open(args[0], "r", "utf-8" )
        except IndexError:
            raise CommandError('No dictionary file specified')
        except IOError:
            raise CommandError('Dictionary file "%s" not found' % args[0])
        
        verbosity = int(options['verbosity'])
        
        self.numberOfImports = 0
        self.numberOfErrors = 0
        self.numberOfWarnings = 0
        
        lineNo = 0
        for line in f.read().splitlines():
            lineNo += 1
            try:
                for word in readWord(line):
                    if '#' in word['untranslated']:
                        # ignore rows where the untranslated word has some # in it. These lines need to be fixed
                        self.error("Invalid characters ('#') in untranslated: %s" % word['untranslated'])
                        continue
                    try:
                        validateBraille(word['braille'])
                        makeWord(word).save()
                        self.numberOfImports += 1
                    except IntegrityError:
                        self.error(lineNo, 'Duplicate word "%s"' % word)
                    except Exception as e:
                        self.error(lineNo, e)
            except Exception as e:
                self.error(lineNo, e)
        
        f.close()
        if verbosity >= 1:
            self.log("\n%s words were successfully updated" % self.numberOfImports)
            if self.numberOfErrors > 0:
                self.log("%s errors" % self.numberOfErrors)
            if self.numberOfWarnings > 0:
                self.log("%s warnings" % self.numberOfWarnings)

    def log(self, message):
        self.stdout.write("%s\n" % message)

    def warning(self, lineNo, message):
        self.numberOfWarnings += 1
        self.log(color.WARNING + "[WARNING] (line %d) %s" % (lineNo, message) + color.END)

    def error(self, lineNo, message):
        self.numberOfErrors += 1
        self.log(color.ERROR + "[ERROR] (line %d) %s" % (lineNo, message) + color.END)
        
class color:
    INSERTED = '\033[1m\033[94m'
    WARNING = '\033[1m\033[93m'
    ERROR = '\033[1m\033[91m'
    DELETED = '\033[1m\033[91m'
    END = '\033[0m\033[0m'

