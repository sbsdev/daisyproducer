# coding=utf-8
import codecs
from optparse import make_option

from daisyproducer.dictionary.models import GlobalWord
from daisyproducer.dictionary.forms import VALID_BRAILLE_RE
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

typeMap = {
    '*': 0, # No restriction
    'd': 0, # Dialect
    'n': 1, # Also as a name
    'N': 2, # Only as a name
    'p': 3, # Also as a place
    'P': 4, # Only as a place
    'H': 5, # Homograph default
    'h': 5, # Homograph alternative
    }

class Command(BaseCommand):
    args = 'dictionary_file'
    help = 'Import the given file as a dictionary'

    option_list = BaseCommand.option_list + (
        make_option(
            '-g',
            '--grade',
            type="int",
            help='Grade for which the words should be applied.'),
        make_option(
            '-f',
            '--format',
            type='choice',
            choices=('2_COLUMN','4_COLUMN'),
            help='Input format'))

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

        self.numberOfWords = 0
        grade = options['grade']
        in_format = options['format']

        if not grade:
            print "No grade specified. No words will be updated"
            return
        if not in_format:
            print "No input format specified. No words will be updated"
            return
        
        for line in f:
            if in_format == '4_COLUMN':
                (typeString, untranslated, braille2, braille1) = line.split()
                braille = braille1 if grade == 1 else braille2
                wordType = (typeMap[typeString],)
            else:
                (untranslated, braille) = line.split()
                wordType = (0,1,2,3,4)
            
            if not VALID_BRAILLE_RE.search(braille):
                print "Invalid characters in Braille (grade %s): %s, %s" % (grade, untranslated, braille)
                continue
            words = GlobalWord.objects.filter(untranslated=untranslated.replace('|',''), grade=grade,
                                             type__in=wordType, 
                                             homograph_disambiguation=untranslated if wordType == 5 else '')
            if words.count() == 0:
                print "Word could not be found in the global dictionary for grade %s: %s" % (grade, untranslated)
                continue
            if words.count() > 1:
                print "Word was found more than once in global dictionary for grade %s: %s (types %s)" % (grade, untranslated, ' + '.join([str(word.type) for word in words]))
                continue
            words.update(braille=braille)
            self.numberOfWords += 1
        
        self.stdout.write('Successfully update %s words\n' % self.numberOfWords)

