
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
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
        form = TripForm(request.POST, request.FILES)
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
def my_reviews(request):
    reviews = Review.objects.filter(user=request.user).select_related('trip')
    return render(request, 'diary/my_reviews.html', {'reviews': reviews})

def travel_map(request):
    return render(request, 'diary/map.html')