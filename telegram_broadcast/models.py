from django.db import models
from account.models import Account
from botpanel.models import BotMessage
from groups.models import Group


class Broadcast(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, verbose_name="Аккаунт")
    text = models.TextField(verbose_name="Текст сообщения, для ссылки используйте запись: \n"
                                         "[нажми сюда](https://example.com)\n"
                                         "Все виды записей: https://core.telegram.org/bots/api#formatting-options:~:text=MarkdownV2%20style,the%20expandability%20mark%7C%7C", null=True, blank=True)

    message_to_forward = models.ForeignKey(
        BotMessage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Сообщение, которое будет разослано"
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Участникам какой группы?"
    )

    button_text = models.CharField(max_length=100, null=True, blank=True, verbose_name="Текст кнопки")
    button_url = models.URLField(null=True, blank=True, verbose_name="Ссылка кнопки")

    photo = models.ImageField(upload_to="broadcasts/photos/", null=True, blank=True, verbose_name="Фото")
    video = models.FileField(upload_to="broadcasts/videos/", null=True, blank=True, verbose_name="Видео")
    audio = models.FileField(upload_to="broadcasts/audios/", null=True, blank=True, verbose_name="Аудио")
    is_video_note = models.BooleanField(verbose_name="Видео (кружок)", default=False, help_text="Отправить как видеосообщение (кружок)")
    is_voice_note = models.BooleanField(verbose_name="Голосовое (только .ogg)", default=False, help_text="Отправить как голосовое сообщение")
    is_sent = models.BooleanField(default=False, verbose_name="Разослано")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def __str__(self):
        return f"Рассылка #{self.pk} от {self.account.phone_number}"
