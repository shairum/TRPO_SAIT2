from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse   # Добавляем этот импорт
from .models import Trip, Review, UserProfile, TripPhoto
from .forms import ReviewForm, CustomUserCreationForm, TripForm, UserProfileForm, UserUpdateForm
from django.shortcuts import render, redirect
import json
import hashlib
import hmac
import time
import random
import string
from django.core.cache import cache
from .models import UserProfile


def generate_telegram_code():
    """Генерирует 6-значный код для Telegram"""
    return ''.join(random.choices(string.digits, k=6))


def telegram_code_login(request):
    """Обработка входа по коду из Telegram"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('telegram_code')

            if code and len(code) == 6 and code.isdigit():
                # Ищем данные по коду в кэше
                code_data = cache.get(f'telegram_code_{code}')
                if code_data:
                    # Создаем или находим пользователя
                    username = f"telegram_{code_data['user_id']}"
                    try:
                        user = User.objects.get(username=username)
                    except User.DoesNotExist:
                        user = User.objects.create_user(
                            username=username,
                            first_name=code_data.get('first_name', ''),
                            password=None
                        )
                        # Создаем профиль
                        UserProfile.objects.create(user=user)

                    # Логиним пользователя с указанием бэкенда
                    from django.contrib.auth import login
                    from django.contrib.auth.backends import ModelBackend
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)

                    # Удаляем использованный код
                    cache.delete(f'telegram_code_{code}')

                    return JsonResponse({'status': 'success', 'redirect_url': '/'})

            return JsonResponse({'status': 'error', 'message': 'Неверный или просроченный код'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def telegram_login(request):
    """Обработка входа через Telegram"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            telegram_data = data.get('telegram_data')

            if telegram_data:
                # Проверяем данные Telegram (упрощенная версия)
                user = authenticate(request, telegram_data=telegram_data)
                if user:
                    login(request, user)
                    return JsonResponse({'status': 'success', 'redirect_url': '/'})

            return JsonResponse({'status': 'error', 'message': 'Ошибка аутентификации'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def telegram_auth(request):
    """Страница для Telegram аутентификации"""
    from django.conf import settings
    return render(request, 'diary/telegram_auth.html', {
        'bot_username': settings.TELEGRAM_BOT_NAME
    })

def home(request):
    sort_by = request.GET.get('sort', '-start_date')
    search_query = request.GET.get('search', '')

    trips_list = Trip.objects.all()

    if search_query:
        trips_list = trips_list.filter(
            Q(title__icontains=search_query) |
            Q(country__icontains=search_query)
        )

    # Простая сортировка без сложных аннотаций
    if sort_by == 'reviews':
        # Сортируем в Python по количеству отзывов
        trips_list = list(trips_list)
        trips_list.sort(key=lambda x: x.reviews_count, reverse=True)
    elif sort_by == 'rating':
        # Сортируем в Python по рейтингу
        trips_list = list(trips_list)
        trips_list.sort(key=lambda x: x.average_rating, reverse=True)
    else:
        trips_list = trips_list.order_by(sort_by)

    paginator = Paginator(trips_list, 8)
    page = request.GET.get('page')

    try:
        trips = paginator.page(page)
    except PageNotAnInteger:
        trips = paginator.page(1)
    except EmptyPage:
        trips = paginator.page(paginator.num_pages)

    return render(request, 'diary/home.html', {
        'trips': trips,
        'sort_by': sort_by,
        'search_query': search_query
    })


def top_rated_trips(request):
    """Упрощенная версия страницы рейтинга"""
    all_trips = Trip.objects.all()
    trips_with_reviews = [trip for trip in all_trips if trip.reviews_count > 0]

    # Сортируем по среднему рейтингу
    trips_with_reviews.sort(key=lambda x: x.average_rating, reverse=True)

    trips = trips_with_reviews[:10]

    return render(request, 'diary/top_rated.html', {
        'trips': trips,
        'title': '🏆 Лучшие поездки по рейтингу'
    })


def most_reviewed_trips(request):
    """Упрощенная версия самых обсуждаемых"""
    all_trips = Trip.objects.all()
    trips_with_reviews = [trip for trip in all_trips if trip.reviews_count > 0]

    # Сортируем по количеству отзывов
    trips_with_reviews.sort(key=lambda x: x.reviews_count, reverse=True)

    trips = trips_with_reviews[:10]

    return render(request, 'diary/top_rated.html', {
        'trips': trips,
        'title': '💬 Самые обсуждаемые поездки'
    })


def trip_detail(request, pk):
    trip = get_object_or_404(Trip, pk=pk)
    reviews = trip.reviews.filter(is_approved=True)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Для добавления отзыва необходимо авторизоваться.')
            return redirect('login')

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.trip = trip

            if Review.objects.filter(user=request.user, trip=trip).exists():
                messages.error(request, 'Вы уже оставляли отзыв на эту поездку.')
            else:
                review.save()
                messages.success(request, 'Ваш отзыв успешно добавлен!')
                return redirect('trip_detail', pk=pk)
    else:
        form = ReviewForm()

    return render(request, 'diary/trip_detail.html', {
        'trip': trip,
        'reviews': reviews,
        'form': form
    })


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}! Регистрация прошла успешно.')
            return redirect('home')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'diary/register.html', {'form': form})


@login_required
def profile(request):
    user_profile = request.user.profile
    user_trips = Trip.objects.filter(user=request.user)
    user_reviews = Review.objects.filter(user=request.user)

    return render(request, 'diary/profile.html', {
        'profile': user_profile,
        'user_trips': user_trips,
        'user_reviews': user_reviews
    })


@login_required
def add_trip(request):
    if request.method == 'POST':
        form = TripForm(request.POST)
        if form.is_valid():
            trip = form.save(commit=False)
            trip.user = request.user
            trip.save()

            # Обработка загруженных фотографий
            photos = request.FILES.getlist('photos')
            for photo in photos:
                TripPhoto.objects.create(trip=trip, image=photo)

            messages.success(request, 'Поездка успешно добавлена!')
            return redirect('trip_detail', pk=trip.pk)
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = TripForm()

    return render(request, 'diary/add_trip.html', {'form': form})


@login_required
def edit_trip(request, pk):
    trip = get_object_or_404(Trip, pk=pk)

    # Проверяем, что пользователь является автором поездки
    if trip.user != request.user:
        messages.error(request, 'Вы можете редактировать только свои поездки.')
        return redirect('trip_detail', pk=pk)

    if request.method == 'POST':
        form = TripForm(request.POST, instance=trip)
        if form.is_valid():
            form.save()

            # Обработка новых фотографий
            photos = request.FILES.getlist('photos')
            for photo in photos:
                TripPhoto.objects.create(trip=trip, image=photo)

            messages.success(request, 'Поездка успешно обновлена!')
            return redirect('trip_detail', pk=pk)
    else:
        form = TripForm(instance=trip)

    return render(request, 'diary/edit_trip.html', {
        'form': form,
        'trip': trip
    })


@login_required
def delete_trip(request, pk):
    trip = get_object_or_404(Trip, pk=pk)

    # Проверяем, что пользователь является автором поездки
    if trip.user != request.user:
        messages.error(request, 'Вы можете удалять только свои поездки.')
        return redirect('trip_detail', pk=pk)

    if request.method == 'POST':
        trip.delete()
        messages.success(request, 'Поездка успешно удалена!')
        return redirect('home')

    return render(request, 'diary/delete_trip.html', {'trip': trip})


@login_required
def edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk)

    # Проверяем, что пользователь является автором отзыва
    if review.user != request.user:
        messages.error(request, 'Вы можете редактировать только свои отзывы.')
        return redirect('trip_detail', pk=review.trip.pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Отзыв успешно обновлен!')
            return redirect('trip_detail', pk=review.trip.pk)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'diary/edit_review.html', {
        'form': form,
        'review': review
    })


@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    trip_pk = review.trip.pk

    # Проверяем, что пользователь является автором отзыва
    if review.user != request.user:
        messages.error(request, 'Вы можете удалять только свои отзывы.')
        return redirect('trip_detail', pk=trip_pk)

    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Отзыв успешно удален!')
        return redirect('trip_detail', pk=trip_pk)

    return render(request, 'diary/delete_review.html', {'review': review})


@login_required
def my_reviews(request):
    reviews = Review.objects.filter(user=request.user).select_related('trip')
    return render(request, 'diary/my_reviews.html', {'reviews': reviews})


def travel_map(request):
    return render(request, 'diary/map.html')


@login_required
def edit_profile(request):
    """Редактирование профиля пользователя"""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Ваш профиль успешно обновлен!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)

    return render(request, 'diary/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@login_required
def delete_avatar(request):
    """Удаление аватара"""
    if request.method == 'POST':
        profile = request.user.profile
        if profile.avatar:
            profile.avatar.delete(save=False)
            profile.avatar = None
            profile.save()
            messages.success(request, 'Фото профиля удалено!')
        return redirect('edit_profile')

    return render(request, 'diary/delete_avatar.html')