# coding=utf-8
import codecs
import os.path
import sys
import tempfile

from collections import namedtuple

import louis

from daisyproducer.dictionary.models import LocalWord
from django.utils.encoding import smart_unicode

TABLES_DIR = os.path.abspath("/usr/local/share/liblouis/tables")

GRADE1_TABLES = ['sbs-wordsplit.dis', 'sbs-de-core6.cti', 'sbs-de-accents.cti', 
                 'sbs-special.cti', 'sbs-whitespace.mod', 'sbs-de-letsign.mod', 
                 'sbs-numsign.mod', 'sbs-litdigit-upper.mod', 'sbs-de-core.mod', 
                 'sbs-de-g1-core.mod', 'sbs-special.mod']

GRADE2_TABLES = GRADE1_TABLES[:]
GRADE2_TABLES[8:10] = ('sbs-de-g2-core.mod',)

GRADE2_TABLES_NAME = GRADE2_TABLES[:]
GRADE2_TABLES_NAME[8:10] = ('sbs-de-g2-name.mod',)

GRADE2_TABLES_PLACE = GRADE2_TABLES[:]
GRADE2_TABLES_PLACE[8:10] = ('sbs-de-g2-place.mod', 'sbs-de-g2-name.mod')

def getTables(grade, name=False, place=False):
    if grade == 1:
        return GRADE1_TABLES
    else:
        if place:
            return GRADE2_TABLES_PLACE
        elif name:
            return GRADE2_TABLES_NAME
        else:
            return GRADE2_TABLES

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
    # P36 ohne nachfolgende Trennmarke "m" (für "ver" u.ä.)
    # Note: in the SBS braille tables this dot pattern is represented by
    # the ascii character 'v'. The reason for this inconsistency is that
    # transcribers want to have a '-' in the user interface. Because the
    # dictionary doesn't contain normal P36, we can savely use '-' instead
    # of 'v' in the database. This is more convenient than having a discordancy
    # between the user interface and the database.
    u'-': "36a", 
    u'ā': "4-1",
    u'ă': "4-1",
    u'ą': "4-1",
    u'ć': "4-14",
    u'ĉ': "4-14",
    u'ċ': "4-14",
    u'č': "4-14",
    u'ď': "4-145",
    u'đ': "4-145",
    u'ē': "4-15",
    u'ė': "4-15",
    u'ę': "4-15",
    u'ğ': "4-1245",
    u'ģ': "4-1245",
    u'ĥ': "4-125",
    u'ħ': "4-125",
    u'ĩ': "4-24",
    u'ī': "4-24",
    u'į': "4-24",
    u'ı': "4-24",
    u'ĳ': "4-245",
    u'ĵ': "4-245",
    u'ķ': "4-13",
    u'ĺ': "4-123",
    u'ļ': "4-123",
    u'ľ': "4-123",
    u'ŀ': "4-123",
    u'ł': "4-123",
    u'ń': "4-1345",
    u'ņ': "4-1345",
    u'ň': "4-1345",
    u'ŋ': "4-1345",
    u'ō': "4-135",
    u'ŏ': "4-135",
    u'ő': "4-135",
    u'ŕ': "4-1235",
    u'ŗ': "4-1235",
    u'ř': "4-1235",
    u'ś': "4-234",
    u'ŝ': "4-234",
    u'ş': "4-234",
    u'š': "4-234",
    u'ţ': "4-2345",
    u'ť': "4-2345",
    u'ŧ': "4-2345",
    u'ũ': "4-136",
    u'ū': "4-136",
    u'ŭ': "4-136",
    u'ů': "4-136",
    u'ű': "4-136",
    u'ų': "4-136",
    u'ŵ': "4-2456",
    u'ŷ': "4-13456",
    u'ź': "4-1356",
    u'ż': "4-1356",
    u'ž': "4-1356",
    u'ǎ': "4-1",
    u'ẁ': "4-2456",
    u'ẃ': "4-2456",
    u'ẅ': "4-2456",
    u'ỳ': "4-13456",
    }

# register a special handler which translates unknown utf-8 into
# \xhhhh escape sequences so liblouis can understand them.
backslashreplace_handler = codecs.lookup_error('backslashreplace')
def liblouis_handler(error):
    (replacement, pos) = backslashreplace_handler(error)
    return (replacement.replace('\u','\\x'), pos)
codecs.register_error('liblouis', liblouis_handler)

def word2dots(word):
    dots = [asciiToDotsMap[c] for c in word]
    return '-'.join(dots)

def writeTable(fileName, words, translate):
    f = codecs.open(os.path.join(TABLES_DIR, fileName), "w", "utf-8", 'liblouis')
    for (untranslated, contracted) in words:
        if translate(smart_unicode(untranslated)) != smart_unicode(contracted):
            # FIXME do we need to translate unichr(0x250A)) back to '|'?
            try:
                f.write("word %s %s\n" % (smart_unicode(untranslated), word2dots(smart_unicode(contracted))))
            except KeyError:
                sys.stderr.write("Error: unknown char in %s (%s, %s)\n" % (contracted, untranslated, fileName))
    f.close()

def writeWhiteListTables(words):
    writeTable('sbs-de-g1-white.mod', 
               ((smart_unicode(word.homograph_disambiguation).replace('|', unichr(0x250A)) if word.type == 5 else word.untranslated, word.braille) 
                for word in words.filter(grade=1)), 
               lambda word: louis.translateString(getTables(1), word))
    writeTable('sbs-de-g2-white.mod', 
               ((smart_unicode(word.homograph_disambiguation).replace('|', unichr(0x250A)) if word.type == 5 else word.untranslated, word.braille) 
                for word in words.filter(grade=2).filter(type__in=(0, 1, 3, 5))), 
               lambda word: louis.translateString(getTables(2), word))
    writeTable('sbs-de-g2-name-white.mod', ((word.untranslated, word.braille) for word in words.filter(grade=2).filter(type__in=(1,2))), 
               lambda word: louis.translateString(getTables(2, name=True), word))
    writeTable('sbs-de-g2-place-white.mod', ((word.untranslated, word.braille) for word in words.filter(grade=2).filter(type__in=(3,4))),
               lambda word: louis.translateString(getTables(2, place=True), word))

def writeLocalTables(changedDocuments):
    for document in changedDocuments:
        words = LocalWord.objects.filter(document=document).order_by('untranslated')
        writeTable('sbs-de-g1-white-%s.mod' % document.identifier, 
                   ((smart_unicode(word.homograph_disambiguation).replace('|', unichr(0x250A)) if word.type == 5 else word.untranslated, word.braille) 
                    for word in words.filter(grade=1)),
                   lambda word: louis.translateString(getTables(1), word))
        writeTable('sbs-de-g2-white-%s.mod' % document.identifier, 
                   ((smart_unicode(word.homograph_disambiguation).replace('|', unichr(0x250A)) if word.type == 5 else word.untranslated, word.braille) 
                    for word in words.filter(grade=2).filter(type__in=(0, 1, 3, 5))),
                   lambda word: louis.translateString(getTables(2), word))
        writeTable('sbs-de-g2-name-white-%s.mod' % document.identifier, 
                   ((word.untranslated, word.braille) for word in words.filter(grade=2).filter(type__in=(1,2))),
                   lambda word: louis.translateString(getTables(2, name=True), word))
        writeTable('sbs-de-g2-place-white-%s.mod' % document.identifier, 
                   ((word.untranslated, word.braille) for word in words.filter(grade=2).filter(type__in=(3,4))),
                  lambda word: louis.translateString(getTables(2, place=True), word))
        
def write_words_with_wrong_default_translation(words):
    from django.forms.models import model_to_dict

    def write_csv(f, tables, word):
        translation = louis.translateString(tables, smart_unicode(word.untranslated))
        if translation != smart_unicode(word.braille):
            d = model_to_dict(word, fields=[field.name for field in word._meta.fields])
            d['translation'] = translation
            f.write("%(untranslated)s\t%(braille)s\t%(translation)s\t%(grade)s\t%(type)s\t%(homograph_disambiguation)s\n" % d)
            
    tmp = tempfile.NamedTemporaryFile(prefix="daisyproducer-", suffix=".csv")
    tmp.close() # we are only interested in a unique filename
    f = codecs.open(tmp.name, "w", "utf-8")

    for word in words:
        if word.grade == 1:
            write_csv(f, getTables(1), word)
        elif word.grade == 2:
            if word.type in (1, 2):
                write_csv(f, getTables(2, name=True), word)
            if word.type in (3, 4):
                write_csv(f, getTables(2, place=True), word)
            if word.type in (0, 1, 3, 5):
                write_csv(f, getTables(2), word)
            
    f.close()
    return tmp.name
