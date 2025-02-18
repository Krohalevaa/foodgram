"""Этот модуль настраивает админ интерфейс для модели `User` в Django."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админ-панель для модели пользователя."""

    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    search_fields = ('email', 'username')
    ordering = ('id',)
    list_filter = ('email',)
