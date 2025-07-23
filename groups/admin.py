from django.contrib import admin
from .models import Group, GroupUser

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("title", "account", "group_id", "last_synced")
    search_fields = ("title",)

@admin.register(GroupUser)
class GroupUserAdmin(admin.ModelAdmin):
    list_display = ("user_id", "username", "first_name", "group", "is_bot")
    search_fields = ("username", "first_name", "last_name")
    list_filter = ("group", "is_bot")
