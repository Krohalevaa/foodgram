# from django.db import models

# # Create your models here.
from django.db import models


class FavoriteRecipe(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='favorite_recipes')
    recipe = models.ForeignKey('recipes.Recipe', on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f"{self.user.username} -> {self.recipe.title}"
