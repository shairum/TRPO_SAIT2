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

    # Telegram аутентификация
    path('telegram-login/', views.telegram_login, name='telegram_login'),
    path('telegram-auth/', views.telegram_auth, name='telegram_auth'),
    path('telegram-code-login/', views.telegram_code_login, name='telegram_code_login'),

    # Личный кабинет
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/delete-avatar/', views.delete_avatar, name='delete_avatar'),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
    path('add-trip/', views.add_trip, name='add_trip'),

    # Редактирование и удаление
    path('trip/<int:pk>/edit/', views.edit_trip, name='edit_trip'),
    path('trip/<int:pk>/delete/', views.delete_trip, name='delete_trip'),
    path('review/<int:pk>/edit/', views.edit_review, name='edit_review'),
    path('review/<int:pk>/delete/', views.delete_review, name='delete_review'),

    # Рейтинги и топы
    path('top-rated/', views.top_rated_trips, name='top_rated'),
    path('most-reviewed/', views.most_reviewed_trips, name='most_reviewed'),
]