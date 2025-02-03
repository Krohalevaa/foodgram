# from django.contrib import admin

# # Register your models here.
from django.contrib import admin
from recipes.models import Recipe, Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}  # Автоматическое создание slug

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name', 'author__username')
    list_filter = ('tags',)
