from django.core.exceptions import ValidationError
from .models import Recipe

def validate_favorite_recipe(user, recipe_id):
    if not user.is_authenticated:
        raise ValidationError("Для добавления рецепта в избранное необходимо войти в систему.")
    
    recipe = Recipe.objects.filter(id=recipe_id).first()
    if not recipe:
        raise ValidationError("Рецепт не найден.")
    
    if user.favorites.filter(recipe=recipe).exists():
        raise ValidationError("Этот рецепт уже добавлен в избранное.")