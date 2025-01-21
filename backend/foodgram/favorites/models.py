from django.db import models


class FavoriteRecipe(models.Model):
    """Модель для избранных рецептов, которые сохраняются пользователем."""
    user = models.ForeignKey('users.User',
                             on_delete=models.CASCADE,
                             related_name='favorite_recipes')
    recipe = models.ForeignKey('recipes.Recipe',
                               on_delete=models.CASCADE,
                               related_name='favorited_by')

    class Meta:
        """Мета-класс для уникальности сочетания пользователя и рецепта."""
        unique_together = ('user', 'recipe')

    def __str__(self):
        """Возвращает строковое представление связи."""
        return f"{self.user.username} -> {self.recipe.title}"
