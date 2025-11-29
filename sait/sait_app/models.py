from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Профиль {self.user.username}"

class Trip(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='trips', 
        verbose_name="Автор",
        db_index=True
    )
    title = models.CharField(max_length=200, verbose_name="Название поездки")
    country = models.CharField(
        max_length=100, 
        verbose_name="Страна",
        db_index=True
    )
    start_date = models.DateField(
        verbose_name="Дата начала",
        db_index=True
    )
    end_date = models.DateField(verbose_name="Дата окончания")
    description = models.TextField(verbose_name="Полный рассказ")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Поездка'
        verbose_name_plural = 'Поездки'
        indexes = [
            models.Index(fields=['user', 'start_date']),
            models.Index(fields=['country']),
            models.Index(fields=['created_at']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('trip_detail', kwargs={'pk': self.pk})

    def average_rating(self):
        """Средний рейтинг поездки"""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 1)
        return 0

    def reviews_count(self):
        """Количество отзывов"""
        return self.reviews.filter(is_approved=True).count()

    def duration_days(self):
        """Продолжительность поездки в днях"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

class TripPhoto(models.Model):
    trip = models.ForeignKey(
        Trip, 
        on_delete=models.CASCADE, 
        related_name='photos',
        db_index=True
    )
    image = models.ImageField(
        upload_to='trip_photos/%Y/%m/%d/', 
        verbose_name="Фотография"
    )
    caption = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name="Подпись"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок отображения"
    )

    class Meta:
        ordering = ['order', 'uploaded_at']
        verbose_name = 'Фотография поездки'
        verbose_name_plural = 'Фотографии поездок'
        indexes = [
            models.Index(fields=['trip', 'order']),
            models.Index(fields=['uploaded_at']),
        ]

    def __str__(self):
        return f"Фото {self.trip.title} ({self.id})"

class Review(models.Model):
    RATING_CHOICES = [
        (1, '⭐ - Плохо'),
        (2, '⭐⭐ - Удовлетворительно'),
        (3, '⭐⭐⭐ - Хорошо'),
        (4, '⭐⭐⭐⭐ - Отлично'),
        (5, '⭐⭐⭐⭐⭐ - Прекрасно'),
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='reviews', 
        verbose_name="Пользователь",
        db_index=True
    )
    trip = models.ForeignKey(
        Trip, 
        on_delete=models.CASCADE, 
        related_name='reviews', 
        verbose_name="Поездка",
        db_index=True
    )
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES, 
        verbose_name="Оценка"
    )
    comment = models.TextField(verbose_name="Комментарий")
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True, verbose_name="Одобрен")

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'trip']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        indexes = [
            models.Index(fields=['user', 'trip']),
            models.Index(fields=['created_at']),
            models.Index(fields=['rating']),
            models.Index(fields=['is_approved']),
        ]

    def __str__(self):
        return f"Отзыв {self.user.username} на {self.trip.title}"

    def get_rating_stars(self):
        """Возвращает звезды рейтинга"""
        return '⭐' * self.rating

    def get_rating_display_short(self):
        """Короткое отображение рейтинга (только звезды)"""
        return '⭐' * self.rating

    @property
    def is_edited(self):
        """Был ли отзыв редактирован"""
        return self.updated_at > self.created_at + timezone.timedelta(seconds=10)