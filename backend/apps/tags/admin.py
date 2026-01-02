from django.contrib import admin
from .models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'type', 'color', 'created_at', 'image_count']
    list_filter = ['type', 'created_at']
    search_fields = ['name']
    ordering = ['name']
    
    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = '图片数量'
