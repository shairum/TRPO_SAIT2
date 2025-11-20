from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.http import Http404
from .models import Trip, Review, UserProfile, TripPhoto
from .forms import ReviewForm, CustomUserCreationForm, TripForm


def home(request):
    trips_list = Trip.objects.all().order_by('-start_date')

    paginator = Paginator(trips_list, 4)
    page = request.GET.get('page')

    try:
        trips = paginator.page(page)
    except PageNotAnInteger:
        trips = paginator.page(1)
    except EmptyPage:
        trips = paginator.page(paginator.num_pages)

    return render(request, 'diary/home.html', {'trips': trips})


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