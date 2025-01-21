from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from recipes.models import Recipe
from .models import Favorite

@login_required
def add_to_favorites(user, recipe_id):
    """
    Проверяет, что пользователь залогинен.
    Ищет рецепт по идентификатору и добавляет его в избранное, если он еще не добавлен.
    """
    recipe = get_object_or_404(Recipe, id=recipe_id)
    Favorite.objects.get_or_create(user=user, recipe=recipe)

@login_required
def remove_from_favorites(user, recipe_id):
    """
    Проверяет, что пользователь залогинен.
    Удаляет рецепт из избранного, если он существует в списке избранного пользователя.
    """
    recipe = get_object_or_404(Recipe, id=recipe_id)
    Favorite.objects.filter(user=user, recipe=recipe).delete()


def get_user_favorites(user):
    """
    Возвращает список избранных рецептов текущего пользователя.
    """
    return Favorite.objects.filter(user=user).select_related('recipe')