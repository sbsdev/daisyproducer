from daisyproducer.documents.models import Document, Version, Attachment, State
from django.contrib import admin


class VersionInline(admin.TabularInline):
	model = Version

class AttachmentInline(admin.TabularInline):
	model = Attachment

class StateAdmin(admin.ModelAdmin):
	list_display = ('name', 'sort_order',)
	ordering = ('sort_order',)
	search_fields = ('name',)

class DocumentAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'source_publisher', 'state',)
	list_filter = ('author', 'source_publisher', 'state',)
	ordering = ('title', 'state',)
	search_fields = ('title',)
	inlines = [VersionInline, AttachmentInline,]

class VersionAdmin(admin.ModelAdmin):
	list_display = ('created_at',)
	ordering = ('created_at',)

class AttachmentAdmin(admin.ModelAdmin):
	list_display = ('comment', 'mime_type',)

admin.site.register(State,StateAdmin)
admin.site.register(Document,DocumentAdmin)
admin.site.register(Version,VersionAdmin)
admin.site.register(Attachment,AttachmentAdmin)
