"""Модуль с фильтрацией ингредиентов в Django-проекте."""

import django_filters
from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(django_filters.FilterSet):
    """Фильтр для модели Ingredient."""

    name = django_filters.CharFilter(field_name='name',
                                     lookup_expr='icontains')

    class Meta:
        """Метаданные для настройки фильтрации модели Ingredient."""

        model = Ingredient
        fields = ['name']


class RecipeFilter(django_filters.FilterSet):
    """Фильтр для модели Recipe."""

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
        """Метаданные для настройки фильтрации модели Recipe."""

        model = Recipe
        fields = ('author', 'tags')
