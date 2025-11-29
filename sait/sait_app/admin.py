from django.contrib import admin
from django.utils.html import format_html
from .models import UserProfile, Trip, TripPhoto, Review


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'country', 'start_date', 'end_date', 'reviews_count', 'average_rating',
                    'created_at']
    list_filter = ['country', 'start_date', 'created_at']
    search_fields = ['title', 'description', 'country', 'user__username']
    date_hierarchy = 'start_date'
    readonly_fields = ['created_at', 'updated_at']

    def reviews_count(self, obj):
        return obj.reviews_count()

    reviews_count.short_description = 'Отзывов'

    def average_rating(self, obj):
        return obj.average_rating()

    average_rating.short_description = 'Рейтинг'


@admin.register(TripPhoto)
class TripPhotoAdmin(admin.ModelAdmin):
    list_display = ['trip', 'image_preview', 'caption', 'order', 'uploaded_at']
    list_filter = ['uploaded_at', 'trip__country']
    search_fields = ['trip__title', 'caption']
    list_editable = ['order']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "Нет фото"

    image_preview.short_description = 'Превью'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'trip', 'rating_stars', 'created_at', 'is_approved', 'is_edited']
    list_filter = ['rating', 'created_at', 'is_approved']
    search_fields = ['user__username', 'trip__title', 'comment']
    list_editable = ['is_approved']
    readonly_fields = ['created_at', 'updated_at']

    def rating_stars(self, obj):
        return obj.get_rating_stars()

    rating_stars.short_description = 'Рейтинг'

    def is_edited(self, obj):
        return obj.is_edited

    is_edited.short_description = 'Редактирован'
    is_edited.boolean = True