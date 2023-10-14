from django.contrib import admin
from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin
from user.models import User, Subscribe


@register(User)
class UserAdmin(UserAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
    )
    fields = (
        (
            "username",
            "email",
        ),
        (
            "first_name",
            "last_name",
        ),
    )
    fieldsets = []

    search_fields = (
        "username",
        "email",
    )
    list_filter = (
        "first_name",
        "email",
    )

@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
