from daisyproducer.documents.models import Document
from django.contrib import admin

class DocumentAdmin(admin.ModelAdmin):
        list_display = ('title', 'author', 'publisher')
        list_filter = ('author', 'publisher')
        ordering = ('title',)
        search_fields = ('title',)

admin.site.register(Document,DocumentAdmin)
