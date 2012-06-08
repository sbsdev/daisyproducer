from daisyproducer.dictionary.models import GlobalWord, LocalWord
from django.contrib import admin

class GlobalWordAdmin(admin.ModelAdmin):
    list_display = ('untranslated', 'braille', 'grade', 'type', 'homograph_disambiguation')
    ordering = ('untranslated',)
    search_fields = ('untranslated',)

class LocalWordAdmin(admin.ModelAdmin):
    list_display = ('untranslated', 'braille', 'grade', 'type', 'homograph_disambiguation','isConfirmed', 'document')
    ordering = ('untranslated',)
    search_fields = ('untranslated',)

admin.site.register(GlobalWord, GlobalWordAdmin)
admin.site.register(LocalWord, LocalWordAdmin)

