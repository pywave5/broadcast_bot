from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.urls import path
from django.shortcuts import redirect, render, get_object_or_404

from .models import Account
from .views import run_in_new_loop
from telethon import TelegramClient
from telethon.sessions import StringSession
from .forms import GroupSelectionForm
from groups.services.collect import collect_users

async def is_session_valid(account: Account) -> bool:
    try:
        client = TelegramClient(StringSession(account.session_string), account.api_id, account.api_hash)
        await client.connect()
        result = await client.is_user_authorized()
        await client.disconnect()
        return result
    except Exception:
        return False


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "is_active", "created_at", "authorize_link", "collect_users_button")

    fieldsets = (
        (None, {
            'fields': ('phone_number', 'is_active', 'session_string')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'api_id', 'api_hash'),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj is None:  # При создании
            return []
        return ['session_string', 'is_active']

    @method_decorator(never_cache)
    def changelist_view(self, request, extra_context=None):
        for acc in Account.objects.filter(is_active=True):
            try:
                if not run_in_new_loop(is_session_valid(acc)):
                    acc.is_active = False
                    acc.session_string = None
                    acc.save()
            except Exception as e:
                print("Ошибка сеанса: ", e)
        return super().changelist_view(request, extra_context)

    def authorize_link(self, obj):
        if obj.is_active:
            return "✅ Авторизован"
        return format_html(
            '<a class="button btn btn-sm btn-primary" href="{}">Авторизоваться</a>',
            f"/account/{obj.id}/authorize/"
        )
    authorize_link.short_description = "Авторизация"

    def collect_users_button(self, obj):
        if not obj.is_active:
            return "🔒 Не авторизован"
        return format_html(
            '<a class="button btn btn-sm btn-warning" href="{}">Собрать участников</a>',
            f"/admin/account/account/{obj.id}/collect-users-form/"
        )
    collect_users_button.short_description = "Сбор участников"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:account_id>/collect-users-form/',
                self.admin_site.admin_view(self.collect_users_form_view),
                name="account-collect-users-form"
            ),
        ]
        return custom_urls + urls

    def collect_users_form_view(self, request, account_id):
        account = get_object_or_404(Account, id=account_id)

        if not account.is_active:
            self.message_user(request, "Сначала авторизуйтесь!", level=messages.ERROR)
            return redirect("/admin/account/account/")

        if request.method == "POST":
            form = GroupSelectionForm(request.POST, account=account)
            if form.is_valid():
                group = form.cleaned_data['group']
                try:
                    run_in_new_loop(collect_users(account, group))
                    self.message_user(request, f"Участники из {group.title} успешно собраны!", level=messages.SUCCESS)
                    return redirect("/admin/account/account/")
                except Exception as e:
                    self.message_user(request, f"Ошибка при сборе: {e}", level=messages.ERROR)
        else:
            form = GroupSelectionForm(account=account)

        return render(request, "admin/account/collect_users.html", {
            "form": form,
            "title": "Сбор участников",
            "opts": self.model._meta,
            "original": account
        })