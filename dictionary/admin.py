from daisyproducer.dictionary.models import Word
from django.contrib import admin

class WordAdmin(admin.ModelAdmin):
    list_display = ('untranslated', 'braille', 'grade', 'type', 'isConfirmed', 'isLocal')
    ordering = ('untranslated',)
    search_fields = ('untranslated',)

admin.site.register(Word, WordAdmin)

