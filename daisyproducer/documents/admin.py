from daisyproducer.documents.models import Document, Version, Attachment, Image, Product, State
from django.contrib import admin


class VersionInline(admin.TabularInline):
	model = Version

class AttachmentInline(admin.TabularInline):
	model = Attachment

class ImageInline(admin.TabularInline):
	model = Image

class ProductInline(admin.TabularInline):
	model = Product

class StateAdmin(admin.ModelAdmin):
	list_display = ('name', 'all_next_states', 'all_responsible', 'sort_order',)
	ordering = ('sort_order',)
	search_fields = ('name',)

def delete_with_content(modeladmin, request, queryset):
	for obj in queryset:
		obj.delete()

delete_with_content.short_description = "Delete selected items with content"

class DocumentAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'source_publisher', 'source', 'state',)
	date_hierarchy = 'date'
	list_filter = ('state',)
	ordering = ('title', 'state',)
	search_fields = ('title', 'author')
	inlines = [VersionInline, AttachmentInline, ImageInline, ProductInline]
	actions = [delete_with_content]

class VersionAdmin(admin.ModelAdmin):
	list_display = ('created_at',)
	ordering = ('created_at',)

class AttachmentAdmin(admin.ModelAdmin):
	list_display = ('comment', 'mime_type',)

class ImageAdmin(admin.ModelAdmin):
	list_display = ('content',)
	list_filter = ('document',)
	actions = [delete_with_content]

class ProductAdmin(admin.ModelAdmin):
	list_display = ('identifier', 'type', 'document',)
	list_filter = ('type',)
	ordering = ('identifier', 'type', 'document',)
	search_fields = ('identifier',)

admin.site.register(State,StateAdmin)
admin.site.register(Document,DocumentAdmin)
admin.site.register(Version,VersionAdmin)
admin.site.register(Attachment,AttachmentAdmin)
admin.site.register(Image,ImageAdmin)
admin.site.register(Product,ProductAdmin)
