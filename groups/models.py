from django.db import models
from account.models import Account

class Group(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    group_id = models.BigIntegerField()
    access_hash = models.BigIntegerField(null=True, blank=True)
    last_synced = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.title


class GroupUser(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="users")
    user_id = models.BigIntegerField()
    access_hash = models.BigIntegerField(null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    is_bot = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Участник группы"
        verbose_name_plural = "Участники групп"
        unique_together = ("group", "user_id")

    def __str__(self):
        return self.username or f"{self.first_name} {self.last_name}" or str(self.user_id)
