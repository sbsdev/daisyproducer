from daisyproducer.documents.models import Document, Version, Attachment
from django.contrib import admin

class VersionInline(admin.TabularInline):
	model = Version

class AttachmentInline(admin.TabularInline):
	model = Attachment

class DocumentAdmin(admin.ModelAdmin):
        list_display = ('title', 'author', 'publisher', 'state',)
        list_filter = ('author', 'publisher', 'state',)
        ordering = ('title', 'state',)
        search_fields = ('title',)
	inlines = [VersionInline, AttachmentInline,]

class VersionAdmin(admin.ModelAdmin):
        list_display = ('created_at',)
        ordering = ('created_at',)

class AttachmentAdmin(admin.ModelAdmin):
        list_display = ('comment', 'mime_type',)

admin.site.register(Document,DocumentAdmin)
admin.site.register(Version,VersionAdmin)
admin.site.register(Attachment,AttachmentAdmin)
