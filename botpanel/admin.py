from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils.timezone import now
from django.shortcuts import redirect
from .models import BotMessage
from .telegram_sender import send_message_to_channel


@admin.register(BotMessage)
class BotMessageAdmin(admin.ModelAdmin):
    list_display = ("__str__", "sent_at", "send_button")

    readonly_fields = ("sent_at", "message_id")

    def send_button(self, obj):
        if obj.sent_at:
            return "✅ Отправлено"
        return format_html(
            '<a class="button btn btn-sm btn-success" href="{}">Отправить</a>',
            f"/admin/botpanel/botmessage/{obj.id}/send/"
        )
    send_button.short_description = "Действие"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:message_id>/send/",
                self.admin_site.admin_view(self.send_message_view),
                name="botmessage-send",
            ),
        ]
        return custom_urls + urls

    def send_message_view(self, request, message_id):
        from .models import BotMessage
        obj = BotMessage.objects.get(id=message_id)

        try:
            msg_id = send_message_to_channel(obj)
            obj.message_id = msg_id
            obj.sent_at = now()
            obj.save()
            self.message_user(request, "Сообщение успешно отправлено.", level=messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Ошибка отправки: {e}", level=messages.ERROR)

        return redirect("/admin/botpanel/botmessage/")
