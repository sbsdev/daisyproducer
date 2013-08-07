# coding=utf-8
import codecs
import csv
import os
import os.path
import re
from django.db import connection, transaction
from django.utils.encoding import smart_unicode
from django.core.exceptions import ObjectDoesNotExist
from daisyproducer.dictionary.models import GlobalWord, VALID_BRAILLE_RE
from difflib import SequenceMatcher
from itertools import tee, izip
from re import split

typeMap = {
    '*': 0, # No restriction
    'n': 1, # Also as a name
    'N': 2, # Only as a name
    'p': 3, # Also as a place
    'P': 4, # Only as a place
    'H': 5, # Homograph default
}

inverseTypeMap = dict((v,k) for k, v in typeMap.iteritems())

class UTF8Recoder:
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        nxt = self.reader.next()
        return nxt.encode("utf-8")

class UnicodeReader:
    def __init__(self, f, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, **kwds)

    def __iter__(self):
        return self

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

class WordReader:
    def __init__(self, f):
        self.reader = UnicodeReader(f, delimiter='\t')
        self.words = []
        self.lineNo = 0

    def __iter__(self):
        return self

    def currentLine(self):
        return self.lineNo

    def next(self):
        if len(self.words) > 0:
            return self.words.pop(0)
        self.lineNo += 1
        line = self.reader.next()
        try:
            (typeString, untranslated, braille1, braille2) = line
            wordType = typeMap[typeString]
            homograph_disambiguation = untranslated if wordType == 5 else ''
            untranslated = untranslated.replace('|','')
            for grade in [1,2]:
                braille = braille2 if grade == 1 else braille1
                if braille == "":
                    continue
                self.words.append({'type': wordType,
                                   'untranslated': untranslated,
                                   'grade': grade,
                                   'homograph_disambiguation': homograph_disambiguation,
                                   'braille': braille})
        except Exception as e:
            raise Exception("Failed parsing word")
        return self.words.pop(0)

def exportWords(f):
    words = GlobalWord.objects.order_by('untranslated', 'type', 'homograph_disambiguation', 'grade')
    skipNext = False
    for (word,nextWord) in pairwise(words.iterator()):
        if skipNext:
            skipNext = False
            continue
        if sameWordsDifferentGrade(word,nextWord):
            braille1 = word.braille
            braille2 = nextWord.braille
            skipNext = True
        elif word.grade == 1:
            braille1 = word.braille
            braille2 = ""
        else:
            braille1 = ""
            braille2 = word.braille
        typeString = inverseTypeMap[word.type]
        untranslated = word.homograph_disambiguation if word.type == 5 else word.untranslated
        f.write("%s\n" % '\t'.join((typeString,
                                    smart_unicode(untranslated),
                                    smart_unicode(braille2),
                                    smart_unicode(braille1))))

# First look for the same word but with different braille translation, then look for
# the same word but with different type.
def getGlobalWord(word):
    try:
        return GlobalWord.objects.get(
                    untranslated=word['untranslated'],
                    grade=word['grade'],
                    type=word['type'],
                    homograph_disambiguation=word['homograph_disambiguation'])
    except ObjectDoesNotExist:
        try:
            return GlobalWord.objects.get(
                        untranslated=word['untranslated'],
                        grade=word['grade'],
                        braille=word['braille'],
                        homograph_disambiguation=word['homograph_disambiguation'])
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            pass
    raise Exception("Word could not be found in the global dictionary: %s" % word)

cursor = connection.cursor()

def insertTempWord(word):
    INSERT_WORD = """
INSERT INTO dictionary_importglobalword (untranslated, grade, braille, type, homograph_disambiguation)
VALUES (%s, %s, %s, %s, %s)
"""
    cursor.execute(INSERT_WORD, [word[k] for k in ('untranslated', 'grade', 'braille', 'type', 'homograph_disambiguation')])

def clearTempWords():
    cursor.execute("DELETE FROM dictionary_importglobalword")

# Get all the words from dictionary_importglobalword that are not already in dictionary_globalword
def changedOrNewWords():
    CHANGED_WORDS = """
SELECT dictionary_importglobalword.*
FROM dictionary_importglobalword
LEFT JOIN dictionary_globalword
ON  dictionary_importglobalword.untranslated             = dictionary_globalword.untranslated
AND dictionary_importglobalword.grade                    = dictionary_globalword.grade
AND dictionary_importglobalword.type                     = dictionary_globalword.type
AND dictionary_importglobalword.braille                  = dictionary_globalword.braille
AND dictionary_importglobalword.homograph_disambiguation = dictionary_globalword.homograph_disambiguation
WHERE dictionary_globalword.untranslated IS NULL
"""
    cursor.execute(CHANGED_WORDS)
    return [{'untranslated': word[1],
             'braille': word[2],
             'grade': word[3],
             'type': word[4],
             'homograph_disambiguation': word[5]} for word in cursor.fetchall()]

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def validateBraille(braille):
    if not VALID_BRAILLE_RE.search(braille):
        raise Exception("Invalid characters in Braille: '%s'" % braille)

def compareBraille(braille, oldBraille):
    if wordDistance(braille, oldBraille) < 0.8:
        raise Exception("New translation differs too much from the current one")

def sameWordsDifferentGrade(word1, word2):
    return (word1.untranslated == word2.untranslated
        and word1.type == word2.type
        and word1.homograph_disambiguation == word2.homograph_disambiguation
        and word1.grade != word2.grade)
    
def wordDistance(old, new):
    return SequenceMatcher(None, old, new).ratio()

def colorDiff(old, new, deleteTags, insertTags):
    opcodes = SequenceMatcher(None, old, new).get_opcodes()
    return u''.join(old[i1:i2] if tag == 'equal' else (deleteTags[0] + old[i1:i2] + deleteTags[1] + 
                                                       insertTags[0] + new[j1:j2] + insertTags[1])
                   for (tag,i1,i2,j1,j2) in opcodes)

