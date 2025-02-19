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
        lookup_expr='icontains')
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug')
    is_favorited = django_filters.BooleanFilter(
        method='filter_is_favorited')
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        """Фильтруем рецепты по добавлению в избранное."""
        if value:
            return queryset.filter(favorited_by_users__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтруем рецепты по добавлению в список покупок."""
        if value:
            return queryset.filter(shopping_lists__user=self.request.user)
        return queryset
