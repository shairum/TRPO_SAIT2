import os
import sys
import django
import requests
import time
import random
import string

# Добавляем путь к проекту
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sait.settings')
django.setup()

# Импорты ПОСЛЕ настройки Django
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()
from sait_app.models import UserProfile
from django.core.cache import cache


def generate_telegram_code():
    """Генерирует 6-значный код для Telegram"""
    return ''.join(random.choices(string.digits, k=6))


def process_updates(updates):
    """Обработка обновлений от Telegram"""
    for update in updates:
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            text = message.get('text', '').strip()

            if text == '/start':
                # Обработка команды /start
                user_id = message['from']['id']
                username = message['from'].get('username', f"user_{user_id}")
                first_name = message['from'].get('first_name', 'Пользователь')

                print(f"📱 Получен /start от {username} (ID: {user_id})")

                # Генерируем код
                code = generate_telegram_code()

                # Сохраняем в кэш на 10 минут
                cache_key = f'telegram_code_{code}'
                cache_data = {
                    'chat_id': chat_id,
                    'user_id': user_id,
                    'username': username,
                    'first_name': first_name
                }

                # Сохраняем в кэш
                cache.set(cache_key, cache_data, 600)
                print(f"💾 Код сохранен в кэш: {code}")

                # Отправляем код пользователю
                message_text = f"""
🔐 **Код для входа в Дневник путешественника**

Ваш код: `{code}`

Перейдите на сайт и введите этот код для входа.

⏰ Код действителен 10 минут.
📎 Сайт: http://127.0.0.1:8000/telegram-auth/
                """

                send_telegram_message(chat_id, message_text)
                print(f"✅ Отправлен код {code} пользователю {username}")

            elif len(text) == 6 and text.isdigit():
                # Обработка кода
                handle_code_input(chat_id, text)


def handle_code_input(chat_id, code):
    """Обработка ввода кода"""
    print(f"🔍 Поиск кода в кэше: {code}")

    cache_key = f'telegram_code_{code}'
    code_data = cache.get(cache_key)

    print(f"🔍 Результат поиска кода {code}: {code_data}")

    if code_data:
        # Создаем или находим пользователя
        telegram_username = f"telegram_{code_data['user_id']}"

        try:
            user = User.objects.get(username=telegram_username)
            print(f"🔍 Найден существующий пользователь: {telegram_username}")
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=telegram_username,
                first_name=code_data.get('first_name', ''),
                password=None
            )
            # Создаем профиль
            UserProfile.objects.create(user=user)
            print(f"✅ Создан новый пользователь: {telegram_username}")

        # Удаляем использованный код
        cache.delete(cache_key)
        print(f"🗑️ Код {code} удален из кэша")

        # Отправляем подтверждение
        send_telegram_message(chat_id, "✅ **Вход выполнен успешно!**\n\nТеперь вы можете пользоваться сайтом.")
        print(f"🎉 Пользователь {telegram_username} успешно вошел")
    else:
        send_telegram_message(chat_id, "❌ **Неверный код**\n\nПожалуйста, проверьте код и попробуйте снова.")
        print(f"❌ Неверный код: {code}")


def send_telegram_message(chat_id, text):
    """Отправка сообщения через Telegram Bot API"""
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }

    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"❌ Ошибка отправки сообщения: {e}")
        return None


def get_updates(offset=None):
    """Получение обновлений от Telegram"""
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
    url = f"https://api.telegram.org/bot{token}/getUpdates"

    params = {'timeout': 30}
    if offset:
        params['offset'] = offset

    try:
        response = requests.get(url, params=params, timeout=35)
        data = response.json()

        if data.get('ok'):
            return data['result'], True
        else:
            print(f"❌ Ошибка получения обновлений: {data}")
            return [], False
    except Exception as e:
        print(f"❌ Ошибка запроса обновлений: {e}")
        return [], False


def start_bot():
    """Запуск простого бота на основе long polling"""
    token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)

    if not token:
        print("❌ TELEGRAM_BOT_TOKEN не настроен в settings.py")
        return

    print(f"🤖 Запуск простого бота с токеном: {token[:10]}...")
    print("✅ Бот запущен и готов к работе!")
    print("Найдите бота в Telegram и отправьте /start")

    last_update_id = None

    while True:
        try:
            updates, success = get_updates(last_update_id)

            if success and updates:
                process_updates(updates)
                last_update_id = updates[-1]['update_id'] + 1 if updates else last_update_id
            else:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n🛑 Бот остановлен")
            break
        except Exception as e:
            print(f"❌ Ошибка в основном цикле: {e}")
            time.sleep(5)


if __name__ == '__main__':
    start_bot()