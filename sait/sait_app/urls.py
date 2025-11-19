
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('trip/<int:pk>/', views.trip_detail, name='trip_detail'),
    path('map/', views.travel_map, name='travel_map'),

    # Авторизация
    path('login/', auth_views.LoginView.as_view(template_name='diary/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),

    # Личный кабинет
    path('profile/', views.profile, name='profile'),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    path('add-trip/', views.add_trip, name='add_trip'),
]