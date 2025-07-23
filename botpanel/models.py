from django.db import models


class BotMessage(models.Model):
    chat_id = models.BigIntegerField(help_text="ID канала, где опубликовано сообщение")
    message_id = models.IntegerField(null=True, blank=True)
    text = models.TextField(null=True, blank=True, help_text="Текст сообщения")
    video = models.FileField(upload_to="videos/", null=True, blank=True, help_text="Видеофайл (mp4 и др.)")
    is_video_note = models.BooleanField(default=False, help_text="Отправить как видеосообщение (кружок)")
    button_text = models.CharField("Текст кнопки", max_length=100, blank=True, null=True)
    button_url = models.URLField("Ссылка кнопки", blank=True, null=True)
    sent_at = models.DateTimeField("Отправлено", null=True, blank=True)
    hint = models.CharField("Подсказка", max_length=255, blank=True, help_text="Для себя")

    class Meta:
        verbose_name = "Бот"
        verbose_name_plural = "Боты"

    def __str__(self):
        if self.hint:
            return f"{self.hint}"
        elif self.text:
            return self.text[:30]
        elif self.message_id:
            return f"ID: {self.message_id}"
        else:
            return f"Сообщение #{self.id}"