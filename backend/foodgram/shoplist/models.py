from django.db import models


class ShoppingList(models.Model):
    """Модель для списка покупок, где пользователь может добавлять рецепты."""
    user = models.ForeignKey('users.User',
                             on_delete=models.CASCADE,
                             related_name='shopping_lists')
    recipe = models.ForeignKey('recipes.Recipe',
                               on_delete=models.CASCADE,
                               related_name='shopping_lists')

    class Meta:
        """Класс для уникальности сочетания пользователя и рецепта в списке."""
        unique_together = ('user', 'recipe')

    def get_shopping_list(self):
        """Получить список ингредиентов для рецептов в списке покупок."""
        ingredients = {}
        for recipe in self.user.shopping_lists.all():
            for recipe_ingredient in recipe.recipe.ingredients.all():
                if recipe_ingredient.ingredient not in ingredients:
                    ingredients[recipe_ingredient.ingredient] = {
                        'quantity': recipe_ingredient.quantity,
                        'unit': recipe_ingredient.unit
                    }
                else:
                    ingredients[recipe_ingredient.ingredient]['quantity'] += recipe_ingredient.quantity
        return ingredients

    def __str__(self):
        """Возвращает строковое представление списка покупок."""
        return f"Shopping list for {self.user.username} - {self.recipe.title}"
