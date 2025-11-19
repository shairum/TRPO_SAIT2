
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    def __str__(self):
        return f"Профиль {self.user.username}"

class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips', verbose_name="Автор")
    title = models.CharField(max_length=200, verbose_name="Название поездки")
    country = models.CharField(max_length=100, verbose_name="Страна")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    description = models.TextField(verbose_name="Полный рассказ")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('trip_detail', kwargs={'pk': self.pk})

    def average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 1)
        return 0

    def reviews_count(self):
        return self.reviews.filter(is_approved=True).count()

class TripPhoto(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='trip_photos/%Y/%m/%d/', verbose_name="Фотография")
    caption = models.CharField(max_length=200, blank=True, verbose_name="Подпись")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Фото {self.trip.title}"

class Review(models.Model):
    RATING_CHOICES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name="Пользователь")
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='reviews', verbose_name="Поездка")
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name="Оценка")
    comment = models.TextField(verbose_name="Комментарий")
    created_at = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=True, verbose_name="Одобрен")

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'trip']

    def __str__(self):
        return f"Отзыв {self.user.username} на {self.trip.title}"

    def get_rating_stars(self):
        return '⭐' * self.rating