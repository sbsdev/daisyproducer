# coding=utf-8
import codecs
import os.path
from collections import namedtuple

from daisyproducer.dictionary.models import Word
from django.utils.encoding import smart_unicode

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
    u'v': "36a", # P36 ohne nachfolgende Trennmarke "m" (für "ver" u.ä.)
    }

def word2dots(word):
    dots = [asciiToDotsMap[c] for c in word]
    return '-'.join(dots)

def writeTable(fileName, words):
    f = codecs.open(os.path.join(TABLES_DIR, fileName), "w", "latin_1")
    for (untranslated, contracted) in words:
        f.write("word %s %s\n" % (smart_unicode(untranslated), word2dots(smart_unicode(contracted))))
    f.close()

def writeWhiteListTables(words):
    writeTable('sbs-de-g1-white.mod', 
               ((word.homograph_disambiguation if word.type == 5 else word.untranslated, word.braille) 
                for word in words.filter(grade=1).filter(type__in=(0, 1, 3, 5))))
    writeTable('sbs-de-g2-white.mod', 
               ((word.homograph_disambiguation if word.type == 5 else word.untranslated, word.braille) 
                for word in words.filter(grade=2).filter(type__in=(0, 1, 3, 5))))
    writeTable('sbs-de-g2-name-white.mod', ((word.untranslated, word.braille) for word in words.filter(grade=2).filter(type=2)))
    writeTable('sbs-de-g2-place-white.mod', ((word.untranslated, word.braille) for word in words.filter(grade=2).filter(type=4)))

def writeLocalTables(changedDocuments):
    for document in changedDocuments:
        words = Word.objects.filter(documents=document).order_by('untranslated')
        writeTable('sbs-de-g1-white-%s.mod' % document.identifier, 
                   ((word.untranslated, word.braille) for word in words.filter(grade=1).filter(type__in=(0, 1, 3, 5))))
        writeTable('sbs-de-g2-white-%s.mod' % document.identifier, 
                   ((word.untranslated, word.braille) for word in words.filter(grade=2).filter(type__in=(0, 1, 3, 5))))
        writeTable('sbs-de-g2-name-white-%s.mod' % document.identifier, 
                   ((word.untranslated, word.braille) for word in words.filter(grade=2).filter(type=2)))
        writeTable('sbs-de-g2-place-white-%s.mod' % document.identifier, 
                   ((word.untranslated, word.braille) for word in words.filter(grade=2).filter(type= 4)))
        
