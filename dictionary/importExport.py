# coding=utf-8
import codecs
import os
import os.path
import re
from django.utils.encoding import smart_unicode
from django.core.exceptions import ObjectDoesNotExist
from daisyproducer.dictionary.models import GlobalWord, VALID_BRAILLE_RE
from difflib import SequenceMatcher
from itertools import tee, izip
from re import split

# What if we get something that's not in typeMap?
typeMap = {
    '*': 0, # No restriction
    'n': 1, # Also as a name
    'N': 2, # Only as a name
    'p': 3, # Also as a place
    'P': 4, # Only as a place
    'H': 5, # Homograph default
}

inverseTypeMap = dict((v,k) for k, v in typeMap.iteritems())

# Assuming there are only words with grade 1 or grade 2
def exportWords(f):
    words = GlobalWord.objects.order_by('untranslated', 'type', 'homograph_disambiguation', 'grade')
    skipNext = False
    for (word,nextWord) in pairwise(words):
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

def readWord(line):
    try:
        (typeString, untranslated, braille1, braille2) = split('\t', line)
        wordType = typeMap[typeString]
        homograph_disambiguation = untranslated if wordType == 5 else ''
        untranslated = untranslated.replace('|','')
        for grade in [1,2]:
            braille = braille2 if grade == 1 else braille1
            if braille == "":
                continue
            if GlobalWord.objects.filter(
                    type=wordType,
                    untranslated=untranslated,
                    grade=grade,
                    homograph_disambiguation=homograph_disambiguation,
                    braille=braille).count() == 0:
                return {'type': wordType,
                        'untranslated': untranslated,
                        'grade': grade,
                        'homograph_disambiguation': homograph_disambiguation,
                        'braille': braille}
    except Exception:
        raise Exception("Failed parsing word")

def validateBraille(braille):
    if not VALID_BRAILLE_RE.search(braille):
        raise Exception("Invalid characters in Braille: '%s'" % braille)
    
def compareBraille(braille, oldBraille):
    if wordDistance(braille, oldBraille) < 0.8:
        raise Exception("New translation differs too much from the current one")

def findWord(word):
    try:
        return GlobalWord.objects.get(
                    untranslated=word['untranslated'],
                    grade=word['grade'],
                    type=word['type'], 
                    homograph_disambiguation=word['homograph_disambiguation'])
    except ObjectDoesNotExist:
        raise Exception("Word '%s' could not be found in the global dictionary" % word['untranslated'])

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

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

