from django.core.exceptions import ValidationError
from recipes.models import Recipe


def validate_favorite_recipe(user, recipe_id):
    """
    Проверяет, залогинен ли пользователь. Если нет, выбрасывает исключение ValidationError с соответствующим сообщением.
    Ищет рецепт по его идентификатору. Если рецепт не найден, также выбрасывает исключение.
    Проверяет, добавлен ли уже данный рецепт в избранное у пользователя. Если да, то выбрасывает исключение, чтобы предотвратить дублирование.
    """
    if not user.is_authenticated:
        raise ValidationError("Для добавления рецепта в избранное необходимо войти в систему.")
    
    recipe = Recipe.objects.filter(id=recipe_id).first()
    if not recipe:
        raise ValidationError("Рецепт не найден.")
    
    if user.favorites.filter(recipe=recipe).exists():
        raise ValidationError("Этот рецепт уже добавлен в избранное.")