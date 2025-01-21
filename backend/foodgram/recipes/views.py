# from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Recipe
# from .forms import RecipeForm
from .validators import validate_favorite_recipe

def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    
    if request.method == 'POST':
        if 'add_to_favorites' in request.POST:
            try:
                validate_favorite_recipe(request.user, recipe.id)
                request.user.favorites.add(recipe)
                messages.success(request, "Рецепт успешно добавлен в избранное.")
            except ValidationError as e:
                messages.error(request, str(e))
        
        if 'add_to_shopping_list' in request.POST:
            # Логика для добавления в список покупок
            pass

    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe})

def recipe_list(request):
    recipes = Recipe.objects.all()
    return render(request, 'recipes/recipe_list.html', {'recipes': recipes})