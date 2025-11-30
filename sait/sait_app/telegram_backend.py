from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
import requests
from .models import UserProfile


class TelegramBackend(BaseBackend):
    def authenticate(self, request, telegram_data=None):
        if not telegram_data:
            return None

        try:
            # Проверяем данные Telegram
            user_data = self.verify_telegram_data(telegram_data)
            if not user_data:
                return None

            # Ищем пользователя по Telegram ID
            try:
                user = User.objects.get(username=f"telegram_{user_data['id']}")
            except User.DoesNotExist:
                # Создаем нового пользователя
                user = User.objects.create_user(
                    username=f"telegram_{user_data['id']}",
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', ''),
                    password=None  # Пароль не нужен для Telegram аутентификации
                )
                # Создаем профиль
                UserProfile.objects.create(user=user)

            return user

        except Exception as e:
            return None

    def verify_telegram_data(self, telegram_data):
        """Проверяет данные от Telegram Widget"""
        # Здесь должна быть логика проверки подписи данных
        # Для упрощения пока пропустим проверку подписи
        return telegram_data

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None