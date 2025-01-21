# # from django.db import models

# # # Create your models here.
# from django.db import models


# class ShoppingList(models.Model):
#     user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='shopping_lists')
#     recipe = models.ForeignKey('recipes.Recipe', on_delete=models.CASCADE, related_name='shopping_lists')

#     def get_shopping_list(self):
#         ingredients = {}
#         for recipe in self.recipe.ingredients.all():
#             ingredient_entry = RecipeIngredient.objects.get(recipe=self.recipe, ingredient=recipe)
#             if ingredient_entry.ingredient not in ingredients:
#                 ingredients[ingredient_entry.ingredient] = {
#                     'quantity': ingredient_entry.quantity,
#                     'unit': ingredient_entry.unit
#                 }
#             else:
#                 ingredients[ingredient_entry.ingredient]['quantity'] += ingredient_entry.quantity
#         return ingredients

#     def __str__(self):
#         return f"Shopping list for {self.user.username} - {self.recipe.title}"
