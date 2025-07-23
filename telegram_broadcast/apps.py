from django.apps import AppConfig


class TelegramBroadcastConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telegram_broadcast'
    verbose_name = "Рассылка"