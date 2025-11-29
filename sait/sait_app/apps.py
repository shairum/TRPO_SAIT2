# apps.py
from django.apps import AppConfig

class SaitAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sait_app'

    def ready(self):
        # Уберите эту строку, если удалили signals.py
        # import sait_app.signals
        pass