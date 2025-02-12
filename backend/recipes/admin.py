"""
Этот модуль настраивает админ интерфейс для моделей `Tag` и `Recipe` в Django.

Модуль включает регистрацию моделей в админке с настройками отображения и
поиска для каждой модели.

Процесс настройки:
1. Модель `Tag` регистрируется с параметрами для отображения и поиска.
2. Модель `Recipe` также регистрируется с настройками для отображения,
поиска и фильтрации.

Каждая настройка включает описание полей для отображения в админке и указания,
какие поля можно искать.
"""

from django.contrib import admin

from recipes.models import Recipe, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели Tag."""

    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели Recipe."""

    list_display = ('name', 'author')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
