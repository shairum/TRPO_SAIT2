# from django.contrib import admin

from django.contrib import admin
from .models import Trip, TripPhoto

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['title', 'country', 'start_date', 'end_date']
    list_filter = ['country', 'start_date']
    search_fields = ['title', 'country', 'description']


@admin.register(TripPhoto)
class TripPhotoAdmin(admin.ModelAdmin):
    list_display = ['trip', 'image_preview', 'caption']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 100px;" />'
        return "Нет изображения"

    image_preview.allow_tags = True
    image_preview.short_description = "Превью"