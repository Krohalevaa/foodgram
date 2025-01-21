# from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from .models import FavoriteRecipe
from recipes.models import Recipe  # предполагается, что модели рецептов находятся в приложении recipes
from django.contrib import messages


@login_required
def add_to_favorites(request, recipe_id):
    """
    Проверяет, является ли пользователь залогиненным.
    Находит рецепт по recipe_id и добавляет его в избранное.
    Возвращает сообщение об успешном добавлении.
    """
    recipe = get_object_or_404(Recipe, id=recipe_id)
    FavoriteRecipe.objects.get_or_create(user=request.user, recipe=recipe)
    messages.success(request, 'Рецепт добавлен в избранное!')
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def remove_from_favorites(request, recipe_id):
    """
    Проверяет, является ли пользователь залогиненным.
    Находит рецепт по recipe_id и удаляет его из избранного, если он там есть.
    Возвращает сообщения в зависимости от результата операции.
    """
    recipe = get_object_or_404(Recipe, id=recipe_id)
    favorite_recipe = FavoriteRecipe.objects.filter(user=request.user, recipe=recipe).first()
    if favorite_recipe:
        favorite_recipe.delete()
        messages.success(request, 'Рецепт удалён из избранного!')
    else:
        messages.error(request, 'Рецепт не найден в вашем избранном.')
    return redirect(request.META.get('HTTP_REFERER'))


class FavoritesListView(View):
    """
    Отображает список избранных рецептов текущего пользователя.
    Использует метод get, чтобы вернуть HTML-шаблон с избранными рецептами.
    """
    def get(self, request):
        favorite_recipes = FavoriteRecipe.objects.filter(user=request.user).select_related('recipe')
        return render(request, 'favorites/favorites_list.html', {'favorite_recipes': favorite_recipes})