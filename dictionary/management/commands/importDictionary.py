# coding=utf-8
import codecs

from daisyproducer.dictionary.models import Word
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
    'd': 6, # Dialect
    }

def get_word(untranslated, grade1, grade2, type):
    return Word(untranslated=untranslated.replace('|',''), 
                grade1=grade1, grade2=grade2, 
                type=type, isConfirmed=True, 
                homograph_disambiguation=untranslated if type == 5 else '')

class Command(BaseCommand):
    args = 'dictionary file name'
    help = 'Import the given file as a dictionary'
    output_transaction = True

    @transaction.commit_on_success
    def handle(self, *args, **options):
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
                continue
            # remove some unnecessary markup
            untranslated = untranslated.replace('#','')
            grade2 = grade2.replace('z','')
            self.lineNo += 1
            type = typeMap[typeString]

            if 's~' in untranslated:
                # if the untranslated word contains a 's~' then add
                # two entries: one for German and one for Swiss German
                # spelling
                w = get_word(untranslated.replace('s~',u'ß'), grade1.replace(u'§','^'), grade2.replace(u'§',u'ß'), type)
                self.save(w)
                w = get_word(untranslated.replace(u's~',u'ss'), grade1.replace(u'§','SS'), grade2.replace(u'§','^'), type)
                self.save(w)
            elif u'ß' in untranslated:
                # if the untranslated word contains a ß then add a
                # second entry for the swiss german spelling
                w = get_word(untranslated, grade1, grade2, type)
                self.save(w)
                w = get_word(untranslated.replace(u'ß','ss'), grade1.replace(u'^','SS'), grade2.replace(u'ß','^'), type)
                self.save(w)
            else:
                w = get_word(untranslated, grade1, grade2, type)
                self.save(w)
                
        self.stdout.write('Successfully added %s words to dictionary\n' % self.numberOfWords)

    def save(self, word):
        try:
            word.save()
            self.numberOfWords += 1
        except IntegrityError:
            raise CommandError('Duplicate word "%s" (line %s)' % (word, self.lineNo))

