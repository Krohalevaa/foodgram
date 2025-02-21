"""
Этот модуль настраивает админ интерфейс для моделей в Django.

Модуль включает регистрацию моделей в админке с настройками отображения и
поиска для каждой модели.

Каждая настройка включает описание полей для отображения в админке и указания,
какие поля можно искать.
"""

from django.contrib import admin

from recipes.models import (FavoriteRecipe, Ingredient, Recipe,
                            RecipeIngredient, ShoppingList, Subscription, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели Tag."""

    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_display_links = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели Ingredient."""

    list_display = ('name', 'unit')
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели Recipe."""

    list_display = ('name', 'author', 'cooking_time', 'creation_date')
    search_fields = ('name', 'author__username')
    list_filter = ('tags__name', 'author__username')
    autocomplete_fields = ('tags', 'ingredients')
    list_display_links = ('name', 'author')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'author'
        ).prefetch_related(
            'tags', 'ingredients'
        ).distinct()


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """Административный интерфейс для связи RecipeIngredient."""

    list_display = ('recipe', 'ingredient', 'amount')
    search_fields = ('recipe__name', 'ingredient__name')
    list_filter = ('recipe', 'ingredient')
    list_select_related = ('recipe', 'ingredient')


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели FavoriteRecipe."""

    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')
    list_select_related = ('user', 'recipe')


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели ShoppingList."""

    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user__is_active',)
    list_select_related = ('user', 'recipe')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Административный интерфейс для модели Subscription."""

    list_display = ('author', 'subscriber')
    search_fields = ('author__username', 'subscriber__username')
    list_filter = ('author__is_active', 'subscriber__is_active')
    list_select_related = ('author', 'subscriber')
