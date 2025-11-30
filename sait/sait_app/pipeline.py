def create_user_profile(strategy, details, response, user, *args, **kwargs):
    """Создает профиль пользователя после OAuth аутентификации"""
    from .models import UserProfile

    if not hasattr(user, 'profile'):
        UserProfile.objects.create(user=user)

    return {'user': user}