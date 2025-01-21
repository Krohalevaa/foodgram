from django import forms
from recipes.models import Recipe

class AddToFavoritesForm(forms.Form):
    """
    Содержит поле recipe_id, которое является скрытым полем для передачи идентификатора рецепта.
    Метод clean_recipe_id проверяет, существует ли рецепт с данным идентификатором, и если нет, возвращает ошибку валидации.
    """
    recipe_id = forms.ModelChoiceField(queryset=Recipe.objects.all(), widget=forms.HiddenInput())

    def clean_recipe_id(self):
        recipe_id = self.cleaned_data['recipe_id']
        if not Recipe.objects.filter(id=recipe_id.id).exists():
            raise forms.ValidationError('Рецепт не найден.')
        return recipe_id