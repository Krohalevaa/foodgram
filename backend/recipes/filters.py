import django_filters
from recipes.models import Ingredient, Recipe, Tag
from django_filters import rest_framework as filters

class IngredientFilter(django_filters.FilterSet):
    # Устанавливаем поиск по подстроке, игнорируя регистр
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(django_filters.FilterSet):
    author = filters.CharFilter(
        field_name='author__id',
        lookup_expr='icontains'
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug', 
        queryset=Tag.objects.all(),
        to_field_name='slug'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags')
