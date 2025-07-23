from django.contrib import admin, messages
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import redirect, get_object_or_404

from telegram_broadcast.models import Broadcast
from telegram_broadcast.services.send_broadcast import send_broadcast
from account.views import run_in_new_loop


@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ("id", "account", "is_sent", "created_at", "send_now_button")
    readonly_fields = ("is_sent", "created_at")

    def send_now_button(self, obj):
        if obj.is_sent:
            return "✅ Отправлено"
        url = reverse("admin:send_broadcast_now", args=[obj.pk])
        return format_html('<a class="button btn btn-sm btn-success" href="{}">Отправить сейчас</a>', url)
    send_now_button.short_description = "Рассылка"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:broadcast_id>/send-now/', self.admin_site.admin_view(self.send_now_view), name="send_broadcast_now")
        ]
        return custom_urls + urls

    def send_now_view(self, request, broadcast_id):
        broadcast = get_object_or_404(Broadcast, id=broadcast_id)

        if broadcast.is_sent:
            self.message_user(request, "Сообщение уже было отправлено.", level=messages.WARNING)
        else:
            try:
                run_in_new_loop(send_broadcast(broadcast_id))
                self.message_user(request, "Рассылка успешно отправлена!", level=messages.SUCCESS)
            except Exception as e:
                self.message_user(request, f"Ошибка при отправке: {e}", level=messages.ERROR)

        return redirect("/admin/telegram_broadcast/broadcast/")
