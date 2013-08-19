# coding=utf-8
import codecs
from daisyproducer.dictionary.importExport import WordReader, compareBraille, validateBraille, getGlobalWord, colorDiff, insertTempWord, clearTempWords, changedOrNewWords, columnize
from daisyproducer.dictionary.models import GlobalWord
from django.core.management.base import BaseCommand, CommandError
from django.utils.encoding import smart_unicode
from django.db import transaction
from optparse import make_option

inverseTypeMap = { 0: '*', 1: 'n', 2: 'N', 3: 'p', 4: 'P', 5: 'H' }

class Command(BaseCommand):
    args = 'dictionary_file'
    help = 'Update the global dictionary with the given file (which must be encoded in UTF-8)'

    option_list = BaseCommand.option_list + (
        make_option(
            '--dry-run',
            default=False,
            help='Do a simulation before actually performing the import'),
        make_option(
            '--force',
            default=False,
            help='Ignore any warnings and just import the words'),
        )

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

        self.logger = codecs.getwriter(self.stdout.encoding if self.stdout.isatty() else 'utf-8')(self.stdout)

        verbosity = int(options['verbosity'])
        dry_run = options['dry_run']
        force = options['force']

        if not dry_run and not force:
            self.log("Warning: this action cannot be undone. Specify the --dry-run option to do a simulation first.")
            raw_input("Hit Enter to continue, or Ctrl-C to abort.")

        self.numberOfUpdates = 0
        self.numberOfInserts = 0
        self.numberOfErrors = 0
        self.numberOfWarnings = 0

        if dry_run:
            verbosity = 2
        if verbosity >= 1:
            self.log("Adding words to temporary table...")
        clearTempWords()
        reader = WordReader(f)
        while True:
            try:
                word = reader.next()
                validateBraille(word['braille'])
                insertTempWord(word)
            except StopIteration:
                break
            except Exception as e:
                self.log(self.error(e, reader.currentLine()))

        if verbosity >= 1:
            self.log("Updating global words...")
            self.log("==================================================================================================================")
            self.log(columnize(("type", "grade", "untranslated", "braille"), (5,5,50,50)))
            self.log("==================================================================================================================")

        for change in changedOrNewWords():
            try:
                word = None
                try:
                    word = getGlobalWord(change)
                except: pass
                if (word != None):
                    if verbosity >= 1:
                        warning = None
                        if change['type'] != word.type:
                            warning = self.warning("Type changed")
                        else:
                            try:
                                compareBraille(change['braille'], word.braille)
                            except Exception as e:
                                warning = self.warning("Significant change")
                        self.log(columnize((inverseTypeMap[word.type] if change['type'] == word.type else
                                                     color.DELETED + inverseTypeMap[word.type] + color.END + ".." +
                                                     color.INSERTED + inverseTypeMap[change['type']] + color.END,
                                            str(word.grade),
                                            word.untranslated,
                                            colorDiff(word.braille, change['braille'], (color.DELETED, color.END), (color.INSERTED, color.END))),
                                           (5,5,50,50))
                                 + ((" # %s" % warning) if warning != None else ""))
                    if not dry_run:
                        word.braille = change['braille']
                        word.type = change['type']
                        word.save()
                    self.numberOfUpdates += 1
                else:
                    if verbosity >= 1:
                        self.log(color.INSERTED
                                 + columnize((inverseTypeMap[change['type']],
                                              str(change['grade']),
                                              change['untranslated'],
                                              change['braille']),
                                             (5,5,50,50))
                                 + color.END
                                 + " # %s" % self.warning("New word"))
                    if not dry_run:
                        GlobalWord(**change).save()
                    self.numberOfInserts += 1
            except Exception as e:
                self.log(self.error(e))
        
        f.close()
        if verbosity >= 1:
            self.log("==================================================================================================================")
            self.log("%s words were successfully updated" % self.numberOfUpdates)
            self.log("%s words were added" % self.numberOfInserts)
            if self.numberOfErrors > 0:
                self.log("%s errors" % self.numberOfErrors)
            if self.numberOfWarnings > 0:
                self.log("%s warnings" % self.numberOfWarnings)

    def log(self, message):
        self.logger.write(u"%s\n" % smart_unicode(message))

    def warning(self, message, lineNo=0):
        self.numberOfWarnings += 1
        if lineNo > 0:
            message = "(line %d) %s" % (lineNo, message)
        return color.WARNING + "[WARNING] %s" % (message) + color.END

    def error(self, message, lineNo=0):
        self.numberOfErrors += 1
        if lineNo > 0:
            message = "(line %d) %s" % (lineNo, message)
        return color.ERROR + "[ERROR] %s" % (message) + color.END

class color:
    INSERTED = r'[01;32m'
    WARNING = r'[01;33m'
    ERROR = r'[01;31m'
    DELETED = r'[01;31m'
    END = r'[0m'
