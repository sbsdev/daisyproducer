# coding=utf-8
import codecs

from daisyproducer.dictionary.models import GlobalWord
from daisyproducer.dictionary.forms import VALID_BRAILLE_RE
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from django.db import transaction

typeMap = {
    '*': 0, # No restriction
    'n': 1, # Also as a name
    'N': 2, # Only as a name
    'p': 3, # Also as a place
    'P': 4, # Only as a place
    'H': 5, # Homograph default
    'h': 5, # Homograph alternative
    }

def get_word(untranslated, braille, grade, type):
    return GlobalWord(untranslated=untranslated.replace('|',''), 
                braille=braille, grade=grade, type=type, isConfirmed=True, 
                homograph_disambiguation=untranslated if type == 5 else '')

class Command(BaseCommand):
    args = 'default_user_id dictionary_file'
    help = 'Import the given file as a dictionary with the given user_id'
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

        self.numberOfWords = 0
        self.lineNo = 0

        for line in f:
            (typeString, untranslated, grade2, grade1) = line.split()
            if '#' in untranslated:
                # ignore rows where the untranslated word has some # in it. These lines need to be fixed
                print "Invalid characters ('#') in untranslated: %s" % (untranslated,)
                continue
            if not VALID_BRAILLE_RE.search(grade1) or not VALID_BRAILLE_RE.search(grade2):
                print "Invalid characters in Braille: %s, %s, %s" % (untranslated, grade1, grade2)
                continue 
                
            self.lineNo += 1

            if typeString == 'd':
                # assume no restriction for dialect words
                type = 0
            else:
                type = typeMap[typeString]

            w1 = get_word(untranslated, grade1, 1, type)
            w2 = get_word(untranslated, grade2, 2, type)
            self.save(w1, w2)
                
        self.stdout.write('Successfully added %s words to dictionary\n' % self.numberOfWords)

    def save(self, grade1, grade2):
        try:
            grade1.save()
            grade2.save()
            self.numberOfWords += 1
        except IntegrityError:
            raise CommandError('Duplicate word "%s" (line %s)' % (grade1, self.lineNo))

