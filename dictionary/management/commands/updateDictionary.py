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
            action='append',
            type="int",
            help='Grade for which the words should be applied.'),)


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

        if not grade:
            print "No grade specified. No words will be updated"
            return
        
        for line in f:
            
            (typeString, untranslated, braille2, braille1) = line.split()
            wordType = typeMap[typeString]
            
            if 1 in grade:
                # Grade 1
                if not VALID_BRAILLE_RE.search(braille1):
                    print "Invalid characters in Braille (grade 1): %s, %s" % (untranslated, braille1)
                    continue
                w1 = GlobalWord.objects.filter(untranslated=untranslated.replace('|',''), grade=1,
                                               type=wordType, 
                                               homograph_disambiguation=untranslated if wordType == 5 else '')
                if not w1.exists():
                    print "Word could not be found in the global dictionary for grade 1: %s" % untranslated
                    continue
                w1.update(braille=braille1)
                self.numberOfWords += 1
            
            if 2 in grade:
                # Grade 2
                if not VALID_BRAILLE_RE.search(braille2):
                    print "Invalid characters in Braille (grade 2): %s, %s" % (untranslated, braille2)
                    continue 
                w2 = GlobalWord.objects.filter(untranslated=untranslated.replace('|',''), grade=2,
                                               type=wordType, 
                                               homograph_disambiguation=untranslated if wordType == 5 else '')
                if not w2.exists():
                    print "Word could not be found in the global dictionary for grade 2: %s" % untranslated
                    continue
                w2.update(braille=braille2)
                self.numberOfWords += 1
        
        self.stdout.write('Successfully update %s words\n' % self.numberOfWords)

