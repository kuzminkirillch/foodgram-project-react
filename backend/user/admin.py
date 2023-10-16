from django.contrib import admin
from user.models import Subscribe, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Админ-зона пользователя.
    """
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    list_filter = ('email', 'first_name')


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    """
    Админ-зона подписок.
    """
    list_display = ('user', 'author')
