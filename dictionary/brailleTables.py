# coding=utf-8
import codecs
import os.path
from collections import namedtuple

from daisyproducer.dictionary.models import Word
from django.utils.encoding import smart_unicode

class DifferentNumberOfPartsError(Exception):
    def __init__(self, grade1Parts, grade2Parts):
        self.grade1Parts = grade1Parts
        self.grade2Parts = grade2Parts

    def __str__(self):
        return "Not the same number of parts for grade1 (%s) and grade2 (%s)" % (self.grade1Parts, self.grade2Parts)

TABLES_DIR = os.path.abspath("/usr/local/share/liblouis/tables")

asciiToDotsMap = {
    u'A': "1",
    u'B': "12",
    u'C': "14",
    u'D': "145",
    u'E': "15",
    u'F': "124",
    u'G': "1245",
    u'H': "125",
    u'I': "24",
    u'J': "245",
    u'K': "13",
    u'L': "123",
    u'M': "134",
    u'N': "1345",
    u'O': "135",
    u'P': "1234",
    u'Q': "12345",
    u'R': "1235",
    u'S': "234",
    u'T': "2345",
    u'U': "136",
    u'V': "1236",
    u'X': "1346",
    u'Y': "13456",
    u'Z': "1356",
    u'0': "346",
    u'1': "16",
    u'2': "126",
    u'3': "146",
    u'4': "1456",
    u'5': "156",
    u'6': "1246",
    u'7': "12456",
    u'8': "1256",
    u'9': "246",
    u'&': "12346",
    u'%': "123456",
    u'[': "12356",
    u'^': "2346",
    u']': "23456",
    u'W': "2456",
    u',': "2",
    u';': "23",
    u':': "25",
    u'/': "256",
    u'?': "26",
    u'+': "235",
    u'=': "2356",
    u'(': "236",
    u'*': "35",
    u')': "356",
    u'.': "3",
    u'\\': "34",
    u'@': "345",
    u'#': "3456",
    u'"': "4",
    u'!': "5",
    u'>': "45",
    u'$': "46",
    u'_': "456",
    u'<': "56",
    u'-': "36",
    u'\'': "6",
    u'ß': "2346",
    u'§': "2346", # bedingtes Eszett
    u'|': "2346", # Eszett bei groß, schließ, ...
    u'à': "123568",
    u'á': "168",
    u'â': "1678",
    u'ã': "34678",
    u'å': "345678",
    u'æ': "478",
    u'ç': "1234678",
    u'è': "23468",
    u'é': "1234568",
    u'ê': "12678",
    u'ë': "12468",
    u'ì': "348",
    u'í': "1468",
    u'î': "14678",
    u'ï': "124568",
    u'ð': "23458",
    u'ñ': "13458",
    u'ò': "3468",
    u'ó': "14568",
    u'ô': "145678",
    u'õ': "1358",
    u'ø': "24678",
    u'ù': "234568",
    u'ú': "1568",
    u'û': "15678",
    u'ý': "24568",
    u'þ': "12348",
    u'ÿ': "134568",
    u'œ': "246789",
    u'b': "0",
    u'm': "d",
    u't': "e",
    u'w': "f",
    u'a': "ca",
    u'n': "cb",
    u'p': "cd",
    u'k': "ce",
    u'v': "36a", # P36 ohne nachfolgende Trennmarke "m" (für "ver" u.ä.)
    }

def word2dots(word):
    dots = [asciiToDotsMap[c] for c in word]
    return '-'.join(dots)

def writeTable(fileName, words):
    f = codecs.open(os.path.join(TABLES_DIR, fileName), "w", "latin_1")
    for (untranslated, contracted) in words:
        # TODO: drop unwanted hyphenation marks
        f.write("word %s %s\n" % (smart_unicode(untranslated), word2dots(smart_unicode(contracted))))
    f.close()

def writeWhiteListTables(words):
    writeTable('sbs-de-g1-white.mod', 
               ((word.homograph_disambiguation if word.type == 5 else word.untranslated, word.grade1) for word in words if word.type in (0, 1, 3, 5)))
    writeTable('sbs-de-g2-white.mod', 
               ((word.homograph_disambiguation if word.type == 5 else word.untranslated, word.grade2) for word in words if word.type in (0, 1, 3, 5)))
    writeTable('sbs-de-g2-name-white.mod', ((word.untranslated, word.grade2) for word in words if word.type == 2))
    writeTable('sbs-de-g2-place-white.mod', ((word.untranslated, word.grade2) for word in words if word.type == 4))

def writeLocalTables(changedDocuments):
    for document in changedDocuments:
        words = Word.objects.filter(documents=document).order_by('untranslated')
        writeTable('sbs-de-g1-white-%s.mod' % document.identifier, 
                   ((word.untranslated, word.grade1) for word in words if word.type in (0, 1, 3, 5)))
        writeTable('sbs-de-g2-white-%s.mod' % document.identifier, 
                   ((word.untranslated, word.grade2) for word in words if word.type in (0, 1, 3, 5)))
        writeTable('sbs-de-g2-name-white-%s.mod' % document.identifier, 
                   ((word.untranslated, word.grade2) for word in words if word.type == 2))
        writeTable('sbs-de-g2-place-white-%s.mod' % document.identifier, 
                   ((word.untranslated, word.grade2) for word in words if word.type == 4))
        
grade1ToUncontractedMap = {
    '0': u'IE',
    '1': u'AU',
    '2': u'EU',
    '3': u'EI',
    '4': u'CH',
    '5': u'SCH',
    '8': u'ü',
    '9': u'ö',
    '@': u'ä',
    '\\': u'äU',
    ']': u'ST',
    '^': u'ß',
    'n': '',
    't': '',
    }

def uncontract(word):
    return u''.join([grade1ToUncontractedMap.get(c, c) for c in word]).lower()

def writeWordSplitTable(words):
    writeWordSplitTableInternal(words.filter(type__in=(0,5)), 
                                ('sbs-de-g1-wordsplit.mod', 'sbs-de-g2-wordsplit.mod'))
    writeWordSplitTableInternal(words.filter(type__in=(1,2)), 
                                ('sbs-de-name-wordsplit.mod',))
    writeWordSplitTableInternal(words.filter(type__in=(3,4)), 
                                ('sbs-de-place-wordsplit.mod',))

def writeWordSplitTableInternal(words, fileNames):

    def getGrade1(word):
        return contractionMap[word].grade1

    def getGrade2(word):
        return contractionMap[word].grade2

    def getSplitWordLine(opcode, wordParts, getGrade):
        splitMarker = "-%s-" % word2dots("w")
        return "%s %s %s-%s\n" % (opcode, "".join(wordParts), word2dots("w"),
                                  splitMarker.join((getGrade(word) for word in wordParts)))

    begwords, endwords, midwords  = (set(), set(), set())
    contractionMap = {}
    Contraction = namedtuple('Contraction', 'grade1 grade2')
    for word in words:
        grade1Parts = smart_unicode(word.grade1).split('w')
        if len(grade1Parts) <= 1:
            continue
        uncontractedParts = [uncontract(part) for part in grade1Parts]
        grade2Parts = smart_unicode(word.grade2).split('w')
        # filter parts that are shorter than 3 characters
        zipped = [items for items in zip(uncontractedParts, grade1Parts, grade2Parts) if len(items[0]) >= 3]
        if not zipped:
            continue # the word has no word parts that are long enough
        uncontractedParts, grade1Parts, grade2Parts = zip(*zipped)
        if len(grade2Parts) != len(grade1Parts):
            raise DifferentNumberOfPartsError(grade1Parts, grade2Parts)
        for uncontracted, grade1, grade2 in zip(uncontractedParts, grade1Parts, grade2Parts):
            contractionMap[uncontracted] = Contraction(word2dots(grade1), word2dots(grade2)) 
        
        numberOfParts = len(uncontractedParts)
        for i in range(1, numberOfParts):
            begwords.add(tuple(uncontractedParts[0:i]))
            endwords.add(tuple(uncontractedParts[i:numberOfParts]))
            for j in range(i+1, numberOfParts):
                midwords.add(tuple(uncontractedParts[i:j]))

    filehandles = [codecs.open(os.path.join(TABLES_DIR, name), "w", "latin_1") for name in fileNames]
    for opcode, wordSet in (("always", begwords & midwords & endwords), 
                            ("begmidword", (begwords & midwords) - endwords),
                            ("midendword", (midwords & endwords) - begwords),
                            ("begword", begwords - midwords - endwords),
                            ("midword", midwords - begwords - endwords),
                            ("endword", endwords - midwords - begwords)):
        for wordParts in wordSet:
            if 'sbs-de-name-wordsplit.mod' in fileNames or 'sbs-de-place-wordsplit.mod' in fileNames:
                filehandles[0].write(getSplitWordLine(opcode, wordParts, getGrade2))
            else:
                filehandles[0].write(getSplitWordLine(opcode, wordParts, getGrade1))
                filehandles[1].write(getSplitWordLine(opcode, wordParts, getGrade2))
    for handle in filehandles:
        handle.close()
