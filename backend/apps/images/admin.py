from django.contrib import admin
from .models import Image, ImageTag


class ImageTagInline(admin.TabularInline):
    model = ImageTag
    extra = 1
    autocomplete_fields = ['tag']


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'filename', 'owner', 'size', 'width', 'height', 'upload_time', 'is_public', 'exif_parsed', 'tag_count']
    list_filter = ['is_public', 'exif_parsed', 'upload_time', 'owner']
    search_fields = ['filename', 'description', 'owner__username', 'tags__name']
    readonly_fields = ['upload_time', 'size', 'width', 'height', 'exif_parsed']
    ordering = ['-upload_time']
    inlines = [ImageTagInline]
    
    def tag_count(self, obj):
        return obj.tags.count()
    tag_count.short_description = '标签数'


@admin.register(ImageTag)
class ImageTagAdmin(admin.ModelAdmin):
    list_display = ['id', 'image', 'tag', 'created_at']
    list_filter = ['tag', 'created_at']
    search_fields = ['image__filename', 'tag__name']
