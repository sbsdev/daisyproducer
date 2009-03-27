from daisyproducer.documents.models import Document
from django.contrib import admin

class DocumentAdmin(admin.ModelAdmin):
        list_display = ('title', 'author', 'publisher', 'state',)
        list_filter = ('author', 'publisher', 'state',)
        ordering = ('title', 'state',)
        search_fields = ('title',)

admin.site.register(Document,DocumentAdmin)
