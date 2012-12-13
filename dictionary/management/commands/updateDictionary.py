# coding=utf-8
import codecs
from daisyproducer.dictionary.importExport import readWord, validateBraille, compareBraille, findWord, colorDiff
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from optparse import make_option

inverseTypeMap = { 0: '*', 1: 'n', 2: 'N', 3: 'p', 4: 'P', 5: 'H' }

class Command(BaseCommand):
    args = 'dictionary_file'
    help = 'Update the global dictionary with the given file'

    option_list = BaseCommand.option_list + (
        make_option(
            '--dry-run',
            default=False,
            help='Do a simulation before actually performing the import'))

    @transaction.commit_on_success
    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Incorrect number of arguments')
        try:
            f = codecs.open(args[0], "r", "utf-8")
        except IndexError:
            raise CommandError('No dictionary file specified')
        except IOError:
            raise CommandError('Dictionary file "%s" not found' % args[0])
        
        verbosity = int(options['verbosity'])
        dry_run = options['dry_run']
        if not dry_run:
            self.log("Warning: this action cannot be undone. Specify the --dry-run option to do a simulation first.")
            raw_input("Hit Enter to continue, or Ctrl-C to abort.")
        
        self.numberOfUpdates = 0
        self.numberOfErrors = 0
        self.numberOfWarnings = 0
        
        if dry_run:
            self.columnize(("type", "grade", "untranslated", "braille"), (4,5,50,50))
            self.columnize(("----", "-----", "------------", "-------"), (4,5,50,50))
        
        lineNo = 0
        for line in f.read().splitlines():
            lineNo += 1
            try:
                for word in readWord(line):
                    try:
                        oldWord = findWord(word)
                        if word['braille'] == oldWord.braille:
                            continue
                        validateBraille(word['braille'])
                        if dry_run:
                            self.columnize((inverseTypeMap[word['type']], word['grade'], word['untranslated'],
                                            colorDiff(oldWord.braille, word['braille'], (color.DELETED, color.END), (color.INSERTED, color.END))),
                                           (4,5,50,50))
                            compareBraille(word['braille'], oldWord.braille)
                        else:
                            oldWord.braille = word['braille']
                            oldWord.save()
                        self.numberOfUpdates += 1
                    except Exception as e:
                        self.error(lineNo, e)
            except Exception as e:
                self.error(lineNo, e)
        
        f.close()
        if verbosity >= 1:
            self.log("\n%s words were successfully updated" % self.numberOfUpdates)
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
        
    def columnize(self, columns, widths):
        self.log((u"%s" % ' '.join(["{%d:<%d}" % (i, widths[i]) for i in range(len(columns))])).format(*columns))
    
class color:
    INSERTED = '\033[1m\033[94m'
    WARNING = '\033[1m\033[93m'
    ERROR = '\033[1m\033[91m'
    DELETED = '\033[1m\033[91m'
    END = '\033[0m\033[0m'

