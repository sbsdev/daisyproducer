# coding=utf-8
import codecs

from daisyproducer.dictionary.models import Word
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError
from django.db import transaction


typeMap = {
    '*': 0, # No restriction
    'd': 2, # Dialect
    'h': 3, # Homograph default
    'H': 4, # Homograph alternative
    'n': 5, # Also as a name
    'N': 6, # Only as a place
    'p': 7, # Also as a place
    'P': 8, # Only as a place
    }

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
            (typeString, untranslated, grade1, grade2) = line.split()
            self.lineNo += 1
              
            if 's~' in untranslated:
                # if the untranslated word contains a 's~' then add
                # two entries: one for German and one for Swiss German
                # spelling
                w = Word(untranslated=untranslated.replace('s~',u'ß'), grade1=grade1.replace(u'§','^'), grade2=grade2.replace(u'§',u'ß'), 
                         type=typeMap[typeString], isConfirmed=True)
                self.save(w)
                w = Word(untranslated=untranslated.replace(u's~',u'ss'), grade1=grade1.replace(u'§','ss'), grade2=grade2.replace(u'§','^'), 
                         type=typeMap[typeString], isConfirmed=True)
                self.save(w)
            elif u'ß' in untranslated:
                # if the untranslated word contains a ß then add a
                # second entry for the swiss german spelling
                w = Word(untranslated=untranslated, grade1=grade1, grade2=grade2, type=typeMap[typeString], isConfirmed=True)
                self.save(w)
                w = Word(untranslated=untranslated.replace(u'ß','ss'), grade1=grade1.replace(u'^','ss'), grade2=grade2.replace(u'ß','^'), 
                         type=typeMap[typeString], isConfirmed=True)
                self.save(w)
            else:
                w = Word(untranslated=untranslated, grade1=grade1, grade2=grade2, type=typeMap[typeString], isConfirmed=True)
                self.save(w)
                
        self.stdout.write('Successfully added %s words to dictionary\n' % self.numberOfWords)

    def save(self, word):
        try:
            word.save()
            self.numberOfWords += 1
        except IntegrityError:
            raise CommandError('Duplicate word "%s" (line %s)' % (word, self.lineNo))

