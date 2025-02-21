"""Этот модуль настраивает админ интерфейс для модели `User` в Django."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админ-панель для модели пользователя."""

    list_display = ('username', 'email', 'first_name',
                    'last_name', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('id',)
    list_filter = ('is_active', 'is_superuser')
    list_display_links = ('username', 'email')

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'user_permissions',
            'groups')
