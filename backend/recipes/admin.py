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
