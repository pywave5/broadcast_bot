from django.db import models

class Account(models.Model):
    api_id = models.IntegerField(unique=True)
    api_hash = models.CharField(max_length=64)
    session_string = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Аккаунт"
        verbose_name_plural = "Аккаунты"

    def __str__(self):
        return f"Account {self.api_id}"